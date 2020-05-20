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
    regression_amplifier = 2

    weather = [
        [12,15,17,25,30,27,21,15],
        [12,15,17,25,30,27,21,15],
        [12,15,17,25,30,27,21,15],
        [12,15,17,25,30,27,21,15],
        [12,15,17,25,30,27,21,15]
    ]

    def get_weather_common(self, amplifier=1, volatility=0):
        p, q = divmod(self.round_number, 8)
        return c(self.weather[p][q] * amplifier + round(np.random.randn() * volatility))

    def get_weather(self):
        return self.get_weather_common()

    def get_weather_forecat(self):
        return self.get_weather_common(3, 2)


class Subsession(BaseSubsession):
    def creating_session(self):
        for p in self.get_players():
            if p.role() == 'Consumer':
                p.payoff = c(1000)
            else:
                p.payoff = c(3000)


class Group(BaseGroup):
    total_consumption = models.CurrencyField(
        min=0,
        doc="""電気総消費量"""
    )
    total_production = models.CurrencyField(
        min=0,
        doc="""電気総生産量"""
    )

    def set_payoffs(self):
        self.total_consumption = sum([p.consumption for p in self.get_players() if p.role() == 'Consumer'])
        self.total_production = sum([p.production for p in self.get_players() if p.role() == 'Producer'])

        if self.total_production < self.total_consumption: # 需要が供給を上回ったら
            for p in self.get_players():
                if p.role() == 'Consumer':
                    p.payoff -= Constants.penalty
                else:
                    p.payoff -= Constants.penalty * 3
        else: # 需要が供給以下だったら
            for p in self.get_players():
                if p.role() == 'Consumer':
                    regression = max(0, p.in_previous_rounds()[-1].consumption - p.consumption) if Constants.round_number > 1 else 0
                    consumer_minus = max(0, Constants.get_weather() - p.consumption) * Constants.amplifier + regression * Constants.regression_amplifier
                    p.payoff -= p.consumption + consumer_minus
                else:
                    p.payoff -= p.production


class Player(BasePlayer):
    consumption = models.CurrencyField(
        min=0,
        doc="""電気消費量"""
    )

    production = models.CurrencyField(
        min=0,
        doc="""電気生産量"""
    )

    def role(self):
        return 'Producer' if self.id_in_group == 1 else 'Consumer'
