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
        round_idx = self.subsession.round_number-1
        p, q = divmod(round_idx, Constants.num_times)

        time_zones = [
            dict(
                start_time=(24//Constants.num_times)*t,
                end_time=(24//Constants.num_times)*(t+1)-1
            ) for t in range(Constants.num_times)
        ]

        return dict(
            date=p+1,
            **time_zones[q],
            penalty_for_producer=Constants.penalty * 3,
            weather_forecast=self.session.vars['weather_forecast'][p][q] * 3,
            forecast_list=[
                dict(
                    date=p+1 if q+1+idx < Constants.num_times else p+2,
                    **time_zones[(q+1+idx)%Constants.num_times],
                    value=x
                ) for
                    idx,
                    x
                in enumerate(
                    self.session.vars['weather_forecast'].reshape([1, -1])[0][round_idx+1:min([
                        round_idx+4,
                        Constants.num_rounds
                    ])]
                )
            ]
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
