from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from djmoney.models.fields import MoneyField

from wewager.exceptions import BalanceTooLow
from wewager.models import Transaction


class Wallet(models.Model):
    """
    Wallet relates a user to a balance, represented in USD with protections againt
    floating-point errors via the **djmoney** package.

    NOTE: All edits to __balance__ must go through the given classmethods. These
    methods acquire a lock on the row being edited to avoid a race condition.
    Please exercise caution when editing a balance.

    Any test classes that edit and assert on the user's balance should use
    __TransactionTestCase__. This base class does not use transactions for each
    test, allowing you to use refresh_from_db() to update the balance.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    balance = MoneyField(max_digits=10, decimal_places=2, default_currency="USD")

    def get_all_transactions(self):
        return Transaction.objects.filter(wallet=self)

    @classmethod
    def add_balance(cls, user, amount, transaction_type):
        with transaction.atomic():
            wallet = cls.objects.select_for_update().get(user=user)
            wallet.balance += amount
            Transaction.objects.create(
                wallet=wallet, amount=amount, transaction_type=transaction_type
            )
        wallet.save()
        return wallet

    @classmethod
    def deduct_balance(cls, user, amount, transaction_type):
        with transaction.atomic():
            wallet = cls.objects.select_for_update().get(user=user)
            if wallet.balance < amount:
                raise BalanceTooLow()
            wallet.balance -= amount
            Transaction.objects.create(
                wallet=wallet, amount=amount, transaction_type=transaction_type
            )
        wallet.save()
        return wallet

    def __str__(self):
        return f"<Wallet {self.user.username} {self.balance}>"


@receiver(post_save, sender=User)
def create_new_wallet(sender, **kwargs):
    if kwargs.get("created", False):
        user = kwargs.get("instance")
        Wallet.objects.create(user=user, balance=0)
