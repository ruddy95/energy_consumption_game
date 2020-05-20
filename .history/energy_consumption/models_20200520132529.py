# coding: utf-8

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
import numpy as np


author = 'Ryusuke Kumita'

doc = """
電力消費ゲームは気温に応じてクーラーの電気消費量が変化することに注目し、
電気料金の設定によって節電の意思決定に影響を与えられるかを検証するゲームです
"""


class Constants(BaseConstants):
    name_in_url = 'energy_consumption'
    players_per_group = 4
    num_rounds = 40

    amplifier = 2
    penalty = c(40)
    regression_cost = 2

    weather = [
        [12,15,17,25,30,27,21,15],
        [12,15,17,25,30,27,21,15],
        [12,15,17,25,30,27,21,15],
        [12,15,17,25,30,27,21,15],
        [12,15,17,25,30,27,21,15]
    ]


class Subsession(BaseSubsession):
    def creating_session(self):
        error = np.random.randn(5,8)
        self.session.vars['weather_forecast'] = np.array(Constants.weather) + error

        for p in self.get_players():
            if p.role() == 'Consumer':
                self.participant.vars['payoff'] = c(1000)
            else:
                self.participant.vars['payoff'] = c(3000)

    def get_weather(self):
        p, q = divmod(self.round_number, 8)
        return c(Constants.weather[p][q])

    def get_weather_forecast(self):
        p, q = divmod(self.round_number, 8)
        return c(self.session.vars['weather_forecast'][p][q])


class Group(BaseGroup):
    total_consumption = models.CurrencyField(
        min=0,
        doc="""電気総消費量"""
    )
    total_production = models.CurrencyField(
        min=0,
        doc="""電気総生産量"""
    )
    is_blackout = models.BooleanField()

    def set_payoffs(self):
        self.total_consumption = sum([p.consumption for p in self.get_players() if p.role() == 'Consumer'])
        self.total_production = sum([p.production for p in self.get_players() if p.role() == 'Producer'])
        self.is_blackout = self.total_production < self.total_consumption # 需要が供給を上回ったら

        # 停電が起きたら
        if self.is_blackout:
            for p in self.get_players():
                if p.role() == 'Consumer':
                    p.usage = Constants.penalty
                    self.participant.vars['payoff'] -= p.usage
                else:
                    p.usage = Constants.penalty * 3
                    self.participant.vars['payoff'] -= p.usage
        else:
            for p in self.get_players():
                if p.role() == 'Consumer':
                    regression_cost = Constants.regression_cost if self.subsession.round_number > 1 and p.in_previous_rounds()[-1].consumption > p.consumption else 0
                    consumer_minus = max(0, self.subsession.get_weather() - p.consumption) * Constants.amplifier + regression_cost
                    p.usage = p.consumption + consumer_minus
                    self.participant.vars['payoff'] -= p.usage
                else:
                    p.usage = p.production
                    self.participant.vars['payoff'] -= p.usage


class Player(BasePlayer):
    consumption = models.CurrencyField(
        min=0,
        doc="""電気消費量"""
    )

    production = models.CurrencyField(
        min=0,
        doc="""電気生産量"""
    )

    usage = models.CurrencyField()

    def role(self):
        return 'Producer' if self.id_in_group == 1 else 'Consumer'
