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
        return dict(
            penalty_for_producer=Constants.penalty * 3,
            input_label='消費する電力量を入力してください' if self.player.role() == 'Consumer' else '',
            weather_forecast=self.subsession.get_weather_forecast() * 3
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'

    body_text = '他のプレイヤーの入力を待っています。'


class Results(Page):
    pass


page_sequence = [MyPage, ResultsWaitPage, Results]
