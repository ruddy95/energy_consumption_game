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

    money = c(1000)
    endowment = c(1000)

    weather = [
        [12,15,17,25,30,27,21,15],
        [12,15,17,25,30,27,21,15],
        [12,15,17,25,30,27,21,15],
        [12,15,17,25,30,27,21,15],
        [12,15,17,25,30,27,21,15]
    ]

    def get_weather_common(self):
        p, q = divmod(self.num_rounds, 8)
        return self.weather[p][q]

    def get_weather(self):
        np.random.randn()
        self.get_weather_common()

    def get_weather_forecat(self):
        self.get_weather_common()


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_consumption = models.PositiveIntegerField(
        min=0,
        doc="""電気総消費量"""
    )

    def set_payoffs(self):
        self.total_consumption = sum([p.consumption for p in self.get_players() if p.role() == 'Consumer'])
        for p in self.get_players():
            p.


class Player(BasePlayer):
    consumption = models.PositiveIntegerField(
        min=0,
        doc="""電気消費量"""
    )

    production = models.PositiveIntegerField(
        min=0,
        doc="""電気生産量"""
    )

    def role(self):
        return 'Producer' if self.id_in_group == 1 else 'Consumer'
