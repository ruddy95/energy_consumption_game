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
        p, q = divmod(self.subsession.round_number-1, 3) # calc

        time_span = 24 // 3 # calc

        return dict(
            date=p+1,
            start_time=q*time_span,
            end_time=(q+1)*time_span-1,
            penalty_for_producer=Constants.penalty * 3,
            weather_forecast=self.session.vars['weather_forecast'][p][q] * 3,
            forecast_list=[dict(start_time=(q+1+idx)*time_span,end_time=(q+2+idx)*time_span-1,value=x) for idx, x in enumerate(self.session.vars['weather_forecast'][p][q+1:])]
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
