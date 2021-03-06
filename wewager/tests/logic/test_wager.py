from datetime import datetime

import pytz
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from djmoney.money import Money

from wewager.exceptions import BalanceTooLow
from wewager.models import (
    Wallet,
    TransactionType,
    Team,
    Game,
    Wager,
    WagerSide,
    WagerState,
    WagerType
)


def _load_test_data(self):
    self.me = get_user_model().objects.create_user(
        username="myname", email="myname@wewager.io", password="hunter42"
    )
    Wallet.add_balance(self.me, Money(100, "USD"), TransactionType.DEPOSIT)
    self.me.refresh_from_db()
    self.you = get_user_model().objects.create_user(
        username="yourname", email="yourname@wewager.io", password="42hunter"
    )
    Wallet.add_balance(self.you, Money(100, "USD"), TransactionType.DEPOSIT)
    self.you.refresh_from_db()

    self.home = Team.objects.create(city="Philadelphia", name="76ers", abbr="PHI")
    self.away = Team.objects.create(city="Toronto", name="Raptors", abbr="TOR")
    self.game = Game.objects.create(date=datetime.now(pytz.utc))
    self.game.add_team(self.home, -3.5, -140)
    self.game.add_team(self.away, 3.5, 140)

    self.team_data = next(x for x in self.game.team_data if x.team.abbr == "PHI")


class WagerTestClass(TransactionTestCase):
    def setUp(self):
        _load_test_data(self)

    def update(self):
        self.me.refresh_from_db()
        self.you.refresh_from_db()

    def test_sender_win(self):
        wager = Wager.objects.create_wager(
            game=self.game,
            team=self.team_data,
            sender=self.me,
            sender_side=WagerSide.WIN,
            recipient=self.you,
            amount=Money(10, "USD"),
        )
        self.update()
        assert wager != None
        assert wager.status == WagerState.PENDING
        assert self.me.wallet.balance == Money(90, "USD")
        assert self.you.wallet.balance == Money(100, "USD")

        wager.accept()
        assert wager.status == WagerState.ACCEPTED
        self.update()
        assert self.me.wallet.balance == Money(90, "USD")
        assert self.you.wallet.balance == Money(90, "USD")

        wager.game.set_winner(self.home)
        wager.complete()
        self.update()
        assert wager.status == WagerState.COMPLETED
        assert self.me.wallet.balance == Money(110, "USD")
        assert self.you.wallet.balance == Money(90, "USD")

    def test_recipient_win(self):
        wager = Wager.objects.create_wager(
            game=self.game,
            team=self.team_data,
            sender=self.me,
            sender_side=WagerSide.WIN,
            recipient=self.you,
            amount=Money(10, "USD"),
        )
        self.update()
        assert wager != None
        assert wager.status == WagerState.PENDING
        assert self.me.wallet.balance == Money(90, "USD")
        assert self.you.wallet.balance == Money(100, "USD")

        wager.accept()
        self.update()
        assert wager.status == WagerState.ACCEPTED
        assert self.me.wallet.balance == Money(90, "USD")
        assert self.you.wallet.balance == Money(90, "USD")

        wager.game.set_winner(self.away)
        wager.complete()
        self.update()
        assert wager.status == WagerState.COMPLETED
        assert self.me.wallet.balance == Money(90, "USD")
        assert self.you.wallet.balance == Money(110, "USD")

    def test_recipient_decline(self):
        wager = Wager.objects.create_wager(
            game=self.game,
            team=self.team_data,
            sender=self.me,
            sender_side=WagerSide.WIN,
            recipient=self.you,
            amount=Money(10, "USD"),
        )
        self.update()
        assert wager != None
        assert wager.status == WagerState.PENDING
        assert self.me.wallet.balance == Money(90, "USD")
        assert self.you.wallet.balance == Money(100, "USD")

        wager.decline()
        self.update()
        assert wager.status == WagerState.DECLINED
        assert self.me.wallet.balance == Money(100, "USD")
        assert self.you.wallet.balance == Money(100, "USD")

    def test_sender_balance_too_low(self):
        self.assertRaises(
            BalanceTooLow,
            Wager.objects.create_wager,
            game=self.game,
            team=self.team_data,
            sender=self.me,
            sender_side=WagerSide.WIN,
            recipient=self.you,
            amount=Money(1000, "USD"),
        )

    def test_recipient_balance_too_low(self):
        Wallet.deduct_balance(self.you, Money(100, "USD"), TransactionType.WITHDRAWAL)
        self.update()
        wager = Wager.objects.create_wager(
            game=self.game,
            team=self.team_data,
            sender=self.me,
            sender_side=WagerSide.WIN,
            recipient=self.you,
            amount=Money(100, "USD")
        )
        self.update()
        self.assertRaises(
            BalanceTooLow,
            wager.accept
        )


class MoneylineTestClass(TransactionTestCase):
    def setUp(self):
        _load_test_data(self)

        # Sender takes favorite (-140)
        self.wager = Wager.objects.create_wager(
            game=self.game,
            team=self.team_data,
            sender=self.me,
            sender_side=WagerSide.WIN,
            recipient=self.you,
            amount=Money(10, "USD"),
            wager_type=WagerType.MONEYLINE
        )
        self.update()

    def update(self):
        self.me.refresh_from_db()
        self.you.refresh_from_db()

    def test_correct_amount(self):
        assert self.wager.amount == Money(10, "USD")
        assert str(self.wager.recipient_amount) == str(Money(7.14, "USD"))

    def test_balance_deduct(self):
        assert self.me.wallet.balance == Money(90, "USD")
        self.wager.accept()
        self.update()
        assert self.you.wallet.balance == Money(92.86, "USD")

    def test_sender_win(self):
        self.wager.accept()
        self.wager.game.set_winner(self.home)
        self.wager.complete()
        self.update()

        assert self.me.wallet.balance == Money(107.14, "USD")
        assert self.you.wallet.balance == Money(92.86, "USD")

    def test_recipient_win(self):
        self.wager.accept()
        self.wager.game.set_winner(self.away)
        self.wager.complete()
        self.update()

        assert self.me.wallet.balance == Money(90, "USD")
        assert self.you.wallet.balance == Money(110, "USD")