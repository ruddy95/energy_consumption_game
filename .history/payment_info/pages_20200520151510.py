from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants


class PaymentInfo(Page):
    def vars_for_template(self):
        return dict(
            payoff=self.participant.vars['payoff']
        )

page_sequence = [PaymentInfo]
