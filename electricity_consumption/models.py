from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
import math
import numpy as np


author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'electricity_consumption'
    players_per_group = 4
    num_rounds = 15

    repeat_span = 5
    peak_mean_base = 13
    offpeak_mean_base = 7
    alpha_base = 2100
    alpha_amplifier = 50
    profit_per_kw = c(10)

    bonus_consumption_range = (34,46)
    penalty_consumption_range = (30,50)
    consumption_bonus = c(1000)
    consumption_penalty = c(-500)

    blackout_criteria = 46
    blackout_penalty = c(-2000)

    minimum_price = 20


class Subsession(BaseSubsession):
    utility_slider = models.IntegerField()
    is_peak = models.BooleanField()
    peak_mean = models.IntegerField()
    offpeak_mean = models.IntegerField()
    alpha = models.IntegerField()

    def creating_session(self):
        if self.round_number % Constants.repeat_span != 1:
            self.group_randomly(fixed_id_in_group=True)

        self.peak_mean = self.in_round(self.round_number-1).peak_mean if self.round_number % Constants.repeat_span != 1 else Constants.peak_mean_base + np.random.randint(2)
        self.offpeak_mean = self.in_round(self.round_number-1).offpeak_mean if self.round_number % Constants.repeat_span != 1 else Constants.offpeak_mean_base + np.random.randint(2)
        self.alpha = self.in_round(self.round_number-1).alpha if self.round_number % Constants.repeat_span != 1 else np.round(Constants.alpha_base + np.random.randn() * Constants.alpha_amplifier)

        self.set_is_peak()
        self.update_utility()

    def update_utility(self):
        self.utility_slider = self.peak_mean if self.is_peak else self.offpeak_mean
        self.utility_slider += np.round(np.random.randn())

    def utility(self, x):
        return np.round(self.alpha / (1 + np.exp(self.utility_slider - x)))

    def set_is_peak(self):
        if self.round_number % Constants.repeat_span == 1:
            self.is_peak = False
        elif self.round_number % Constants.repeat_span == 2:
            self.is_peak = True
        else:
            self.is_peak = np.random.rand() > .2


class Group(BaseGroup):
    peak_pricing = models.IntegerField(
        min=Constants.minimum_price
    )

    offpeak_pricing = models.IntegerField(
        min=Constants.minimum_price
    )

    is_blackout = models.BooleanField()

    total_consumption = models.CurrencyField()

    def pricing(self):
        n = (self.subsession.round_number - 1) // Constants.repeat_span * Constants.repeat_span + 1
        return self.in_round(n).peak_pricing if self.subsession.is_peak else self.in_round(n).offpeak_pricing

    def set_payoffs(self):
        self.total_consumption = sum([p.consumption for p in self.get_players() if p.role() == 'Consumer'])
        self.is_blackout = self.total_consumption >= Constants.blackout_criteria
        for p in self.get_players():
            if p.role() == 'Producer':
                p.payoff = Constants.profit_per_kw * self.total_consumption
                if self.total_consumption in range(*Constants.bonus_consumption_range):
                    p.payoff += Constants.consumption_bonus
                elif self.total_consumption not in range(*Constants.penalty_consumption_range):
                    p.payoff += Constants.consumption_penalty
            else:
                p.payoff = Constants.blackout_penalty if self.is_blackout else self.subsession.utility(p.consumption)
                if self.subsession.round_number % Constants.repeat_span == 0:
                    repeat_span_idx = self.subsession.round_number // Constants.repeat_span
                    p.payoff -= sum([self.in_round(i).pricing() * p.in_round(i).consumption for i in range((repeat_span_idx - 1) * Constants.repeat_span + 1, repeat_span_idx * Constants.repeat_span + 1)])


class Player(BasePlayer):
    consumption = models.IntegerField(
        min=0
    )

    def role(self):
        return 'Producer' if self.id_in_group == 1 else 'Consumer'
