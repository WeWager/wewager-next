from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField


class TransactionType(models.TextChoices):
    DEPOSIT = "DEP", _("Deposit")
    WITHDRAWAL = "WTH", _("Withdrawal")
    WAGER = "WAG", _("Wager")
    DECLINE = "DEC", _("Decline")
    WIN = "WIN", _("Win")
    EXPIRE = "EXP", _("Expire")


class Transaction(models.Model):
    wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE)
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency="USD")
    transaction_type = models.CharField(max_length=3, choices=TransactionType.choices)

    def __str__(self):
        return f"<Transaction {self.wallet.user.username} {self.amount} {self.transaction_type}>"