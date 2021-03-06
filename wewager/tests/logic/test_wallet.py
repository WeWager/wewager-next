from django.contrib.auth import get_user_model
from django.test import TestCase
from djmoney.money import Money

from wewager.models import Wallet, TransactionType


class WalletTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@wewager.io", password="top_secret"
        )

    def test_add_balance(self):
        self.assertEqual(len(self.user.wallet.get_all_transactions()), 0)
        wallet = Wallet.add_balance(
            self.user, Money(50, "USD"), TransactionType.DEPOSIT
        )
        transactions = wallet.get_all_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(wallet.balance, Money(50, "USD"))

        wallet = Wallet.deduct_balance(
            self.user, Money(50, "USD"), TransactionType.WITHDRAWAL
        )
        self.assertEqual(wallet.balance, Money(0, "USD"))
