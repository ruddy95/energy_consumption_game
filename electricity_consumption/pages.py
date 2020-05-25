from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import numpy as np


class Instruction(Page):
    def is_displayed(self):
        return self.subsession.round_number == 1


class Price(Page):
    form_model = 'group'
    form_fields = ['peak_pricing', 'offpeak_pricing']

    def utility(self, is_peak=False):
        slider = self.subsession.peak_mean if is_peak else self.subsession.offpeak_mean
        return np.round(self.subsession.alpha / (1 + np.exp(slider - self.x_range(is_peak)))).reshape((1,-1)) - np.dot(self.p_range().reshape((-1,1)), self.x_range(is_peak).reshape(1,-1))

    def x_range(self, is_peak=False):
        slider = self.subsession.peak_mean if is_peak else self.subsession.offpeak_mean
        return np.array(range(0, slider + 10))

    def p_range(self):
        return np.array([Constants.minimum_price + 10 * i for i in range(12)])

    def vars_for_template(self):
        return dict(
            peak_x_range=self.x_range(True),
            offpeak_x_range=self.x_range(False),
            calculated_peak_utilities=self.utility(True),
            calculated_offpeak_utilities=self.utility(False)
        )

    def is_displayed(self):
        return self.player.role() == 'Producer' and self.subsession.round_number % Constants.repeat_span == 1


class ConsumeWaitPage(WaitPage):
    pass


class Consume(Page):
    form_model = 'player'
    form_fields = ['consumption']

    def point(self, x):
        return np.round(self.subsession.alpha / (1 + np.exp(self.subsession.utility_slider - x))) - int(self.group.pricing()) * x

    def vars_for_template(self):
        x_range = np.array(range(0, self.subsession.utility_slider + 10))
        return dict(
            x_range=x_range,
            calculated_points=self.point(x_range)
        )

    def is_displayed(self):
        return self.player.role() == 'Consumer'


class ResultWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'


class Results(Page):
    def point(self, x):
        return np.round(self.subsession.alpha / (1 + np.exp(self.subsession.utility_slider - x))) - int(self.group.pricing()) * x

    def vars_for_template(self):
        x_range = np.array(range(max(0,self.subsession.utility_slider - 10), self.subsession.utility_slider + 10))
        return dict(
            x_range=x_range,
            calculated_points=self.point(x_range)
        )


page_sequence = [
    Instruction,
    Price,
    ConsumeWaitPage,
    Consume,
    ResultWaitPage,
    Results
]
