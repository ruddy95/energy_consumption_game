# coding: utf-8

from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class MyPage(Page):
    form_model = 'player'

    def get_form_fields(self):
        if self.player.role() == 'Consumer':
            return ['consumption']
        else:
            return ['production']

    def vars_for_template(self):
        p1, q1 = divmod(self.subsession.round_number-1, 3) # calc
        p2, q2 = divmod(self.subsession.round_number, 3) # calc

        return dict(
            penalty_for_producer=Constants.penalty * 3,
            weather_forecast=self.session.vars['weather_forecast'][p1][q1] * 3,
            forecast_list=map(lambda x: dict(start_time=,end_time=,value=x), self.session.vars['weather_forecast'][p2][q2:])
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'

    body_text = '他のプレイヤーの入力を待っています。'


class Results(Page):
    def vars_for_template(self):
        return dict(
            payoff=self.participant.vars['payoff']
        )


page_sequence = [MyPage, ResultsWaitPage, Results]
