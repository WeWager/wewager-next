from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from rest_framework.exceptions import ParseError

from wewager.exceptions import BalanceTooLow
from wewager.models.game import Game
from wewager.models.transaction import TransactionType
from wewager.models.wallet import Wallet


class WagerManager(models.Manager):
    def create_wager(self, *args, **kwargs):
        sender = kwargs.get("sender")
        amount = kwargs.get("amount")

        if Wallet.deduct_balance(
            sender, amount, transaction_type=TransactionType.WAGER
        ):
            return super(WagerManager, self).create(*args, **kwargs)
        else:
            raise BalanceTooLow()


class WagerState(object):
    PENDING = "pending"
    DECLINED = "declined"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    EXPIRED = "expired"


class WagerType(models.TextChoices):
    NORMAL = "Normal", _("normal")
    SPREAD = "Point Spread", _("spread")
    MONEYLINE = "Moneyline", _("moneyline")


class WagerSide(models.TextChoices):
    WIN = "W", _("Win")
    LOSE = "L", _("Lose")


class Wager(models.Model):
    objects = WagerManager()

    game = models.ForeignKey("Game", on_delete=models.CASCADE)
    outcome = models.ForeignKey("GameOutcome", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipient"
    )
    amount = MoneyField(
        max_digits=7,
        decimal_places=2,
        default_currency="USD",
        validators=[MinMoneyValidator(0)],
    )
    status = FSMField(default=WagerState.PENDING)

    @property
    def recipient_amount(self):
        if self.outcome.bet_type != WagerType.MONEYLINE:
            return self.amount
        price = int(self.outcome.bet_price)
        odds = abs(price)
        sender_favorite = price < 0
        if sender_favorite:
            return (100 / odds) * self.amount
        else:
            return (odds / 100) * self.amount

    @transition(field=status, source=WagerState.PENDING, target=WagerState.ACCEPTED)
    def accept(self):
        Wallet.deduct_balance(
            self.recipient, self.recipient_amount, TransactionType.WAGER
        )

    @transition(field=status, source=WagerState.PENDING, target=WagerState.DECLINED)
    def decline(self):
        Wallet.add_balance(self.sender, self.amount, TransactionType.DECLINE)

    @transition(field=status, source=WagerState.PENDING, target=WagerState.EXPIRED)
    def expire(self):
        Wallet.add_balance(self.sender, self.amount, TransactionType.EXPIRE)

    @transition(field=status, source=WagerState.ACCEPTED, target=WagerState.COMPLETED)
    def complete(self, outcome_hit):
        winnings = self.amount + self.recipient_amount
        winner = self.sender if outcome_hit else self.recipient
        Wallet.add_balance(winner, winnings, TransactionType.WIN)
