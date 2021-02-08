from enum import Enum

from .exceptions import BalanceTooLow

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework.exceptions import ParseError
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from djmoney.money import Money
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from django_fsm import FSMField, transition


class Avatar(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    image = models.ImageField(upload_to="avatars")


class TransactionType(models.TextChoices):
    DEPOSIT = "DEP", _("Deposit")
    WITHDRAWAL = "WTH", _("Withdrawal")
    WAGER = "WAG", _("Wager")
    DECLINE = "DEC", _("Decline")
    WIN = "WIN", _("Win")
    EXPIRE = "EXP", _("Expire")


class Wallet(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True)
    balance = MoneyField(max_digits=10, decimal_places=2, default_currency="USD")

    def get_all_transactions(self):
        return Transaction.objects.filter(wallet=self)

    def add_balance(self, amount, transaction_type):
        self.balance += amount
        Transaction.objects.create(
            wallet=self, amount=amount, transaction_type=transaction_type
        )

    def deduct_balance(self, amount, transaction_type):
        if self.balance < amount:
            raise BalanceTooLow()
        self.balance -= amount
        Transaction.objects.create(
            wallet=self, amount=amount, transaction_type=transaction_type
        )
        return True

    def __str__(self):
        return f"<Wallet {self.user.username} {self.balance}>"


@receiver(post_save, sender=User)
def create_new_wallet(sender, **kwargs):
    if kwargs.get("created", False):
        user = kwargs.get("instance")
        Wallet.objects.create(user=user, balance=0)


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency="USD")
    transaction_type = models.CharField(max_length=3, choices=TransactionType.choices)

    def __str__(self):
        return f"<Transaction {self.wallet.user.username} {self.amount} {self.transaction_type}>"


class Team(models.Model):
    city = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    abbr = models.CharField(max_length=5)

    @property
    def full_name(self):
        return self.city + " " + self.name

    def __str__(self):
        return f"{self.city} {self.name}"


class Game(models.Model):
    date = models.DateTimeField()
    winner = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE)
    data = models.JSONField(null=True, blank=True)

    @property
    def teams(self):
        return [x.team for x in TeamData.objects.filter(game=self)]

    @property
    def team_data(self):
        return TeamData.objects.filter(game=self)

    def add_team(self, team, spread, moneyline):
        return TeamData.objects.create(
            team=team, game=self, spread=spread, moneyline=moneyline
        )

    def set_winner(self, team):
        if team not in self.teams:
            return None
        self.winner = team

    def __str__(self):
        return f"<Game #{self.id}>"


@receiver(post_save, sender=Game)
def close_game(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance is None:
        return
    if instance.winner is not None:
        assoc_wagers = Wager.objects.filter(game=instance)
        for wager in assoc_wagers:
            if wager.status == WagerState.PENDING:
                wager.expire()
            elif wager.status == WagerState.ACCEPTED:
                wager.complete()
            wager.save()


class TeamData(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    spread = models.DecimalField(decimal_places=1, max_digits=3)
    moneyline = models.IntegerField()

    def __str__(self):
        return f"<TeamData {self.team.abbr} {self.game.date}>"


class WagerSide(models.TextChoices):
    WIN = "W", _("Win")
    LOSE = "L", _("Lose")


class WagerType(models.TextChoices):
    NORMAL = "normal", _("normal")
    SPREAD = "spread", _("spread")
    MONEYLINE = "moneyline", _("moneyline")


class WagerState(object):
    PENDING = "pending"
    DECLINED = "declined"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    EXPIRED = "expired"


class WagerManager(models.Manager):
    def create_wager(self, *args, **kwargs):
        sender = kwargs.get("sender", None)
        recipient = kwargs.get("recipient", None)
        if sender == recipient:
            raise ParseError("You cannot send a wager to yourself.")
        amount = kwargs.get("amount", None)
        if (
            sender
            and amount
            and sender.wallet.deduct_balance(amount, TransactionType.WAGER)
        ):
            return super(WagerManager, self).create(*args, **kwargs)
        else:
            raise BalanceTooLow()


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
    status = FSMField(default=WagerState.PENDING)

    @transition(field=status, source=WagerState.PENDING, target=WagerState.ACCEPTED)
    def accept(self):
        self.recipient.wallet.deduct_balance(self.amount, TransactionType.WAGER)
        self.recipient.wallet.save()

    @transition(field=status, source=WagerState.PENDING, target=WagerState.DECLINED)
    def decline(self):
        self.sender.wallet.add_balance(self.amount, TransactionType.DECLINE)
        self.sender.wallet.save()

    @transition(field=status, source=WagerState.PENDING, target=WagerState.EXPIRED)
    def expire(self):
        self.sender.wallet.add_balance(self.amount, TransactionType.EXPIRE)
        self.sender.wallet.save()

    @transition(field=status, source=WagerState.ACCEPTED, target=WagerState.COMPLETED)
    def complete(self):
        if self.game.winner == None:
            return

        winning_side = (
            WagerSide.WIN if self.game.winner == self.team.team else WagerSide.LOSE
        )
        winner = self.sender if self.sender_side == winning_side else self.recipient
        winner.wallet.add_balance(2 * self.amount, TransactionType.WIN)
        winner.wallet.save()
