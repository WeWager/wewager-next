from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from rest_framework.exceptions import ParseError

from wewager.exceptions import BalanceTooLow
from wewager.models.game import Game
from wewager.models.team_data import TeamData
from wewager.models.transaction import TransactionType
from wewager.models.wallet import Wallet


class WagerManager(models.Manager):
    def create_wager(self, *args, **kwargs):
        sender = kwargs.get("sender", None)
        recipient = kwargs.get("recipient", None)
        if sender == recipient:
            raise ParseError("You cannot send a wager to yourself.")
        amount = kwargs.get("amount", None)

        wager_type = kwargs.get("wager_type", None)
        wager_side = kwargs.get("sender_side", None)
        if wager_type == WagerType.MONEYLINE and wager_side == WagerSide.LOSE:
            raise ParseError("You must take the winning side on a moneyline wager.")

        if (
            sender
            and amount
            and Wallet.deduct_balance(
                sender, amount, transaction_type=TransactionType.WAGER
            )
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
    NORMAL = "normal", _("normal")
    SPREAD = "spread", _("spread")
    MONEYLINE = "moneyline", _("moneyline")


class WagerSide(models.TextChoices):
    WIN = "W", _("Win")
    LOSE = "L", _("Lose")


class Wager(models.Model):
    objects = WagerManager()

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(TeamData, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    sender_side = models.CharField(max_length=2, choices=WagerSide.choices)
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipient"
    )
    amount = MoneyField(
        max_digits=7,
        decimal_places=2,
        default_currency="USD",
        validators=[MinMoneyValidator(0)],
    )
    wager_type = models.CharField(
        max_length=10, choices=WagerType.choices, default=WagerType.NORMAL
    )
    status = FSMField(default=WagerState.PENDING)

    @property
    def sender_side_full(self):
        return "Win" if self.sender_side == WagerSide.WIN else "Lose"

    @property
    def recipient_amount(self):
        if self.wager_type != WagerType.MONEYLINE:
            return self.amount
        odds = abs(self.team.moneyline)
        sender_favorite = self.team.moneyline < 0
        if sender_favorite:
            return (100 / odds) * self.amount
        else:
            return (odds / 100) * self.amount

    @transition(field=status, source=WagerState.PENDING, target=WagerState.ACCEPTED)
    def accept(self):
        Wallet.deduct_balance(self.recipient, self.recipient_amount, TransactionType.WAGER)

    @transition(field=status, source=WagerState.PENDING, target=WagerState.DECLINED)
    def decline(self):
        Wallet.add_balance(self.sender, self.amount, TransactionType.DECLINE)

    @transition(field=status, source=WagerState.PENDING, target=WagerState.EXPIRED)
    def expire(self):
        Wallet.add_balance(self.sender, self.amount, TransactionType.EXPIRE)

    @transition(field=status, source=WagerState.ACCEPTED, target=WagerState.COMPLETED)
    def complete(self):
        if self.game.winner == None:
            return

        winning_side = (
            WagerSide.WIN if self.game.winner == self.team.team else WagerSide.LOSE
        )
        winner = self.sender if self.sender_side == winning_side else self.recipient
        if self.wager_type == WagerType.NORMAL:
            payout = 2 * self.amount
        elif self.wager_type == WagerType.MONEYLINE:
            payout = self.amount + self.recipient_amount

        Wallet.add_balance(winner, payout, TransactionType.WIN)
