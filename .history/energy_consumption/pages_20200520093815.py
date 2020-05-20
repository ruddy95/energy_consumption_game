# coding: utf-8

from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class MyPage(Page):
    form_model = 'player'
    form_fields = ['consumption', 'production']

    def vars_for_template(self):
        return dict(
            penalty_for_producer=Constants.penalty * 3,
            weather_forecast=self.session.vars['weather_forecast']
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'

    body_text = '他のプレイヤーの入力を待っています。'


class Results(Page):
    pass


page_sequence = [MyPage, ResultsWaitPage, Results]
