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


author = 'Ryusuke Kumita'

doc = """
電力消費ゲームは気温に応じてクーラーの電気消費量が変化することに注目し、
電気料金の設定によって節電の意思決定に影響を与えられるかを検証するゲームです
"""


class Constants(BaseConstants):
    name_in_url = 'energy_consumption'
    players_per_group = 4
    num_rounds = 30

    money = c(1000)
    endowment = c(1000)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    def set_payoffs(self):



class Player(BasePlayer):
    consumption = models.PositiveIntegerField(
        min=0,
        doc="""電気消費量"""
    )

    def role(self):
        return 'Producer' if self.id_in_group == 1 else 'Consumer'
