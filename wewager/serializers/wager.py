from djmoney.contrib.django_rest_framework import MoneyField
from moneyed import Money
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from wewager.models import Wager


class WagerSerializer(serializers.ModelSerializer):
    opponent = serializers.SerializerMethodField()
    is_sender = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    amount = MoneyField(max_digits=10, decimal_places=2)
    recipient_amount = MoneyField(max_digits=10, decimal_places=2)

    class Meta:
        model = Wager
        fields = (
            "id",
            "game",
            "outcome",
            "sender",
            "opponent",
            "is_sender",
            "recipient_amount",
            "amount",
            "status",
        )

    def get_opponent(self, wager):
        opp = (
            wager.sender
            if wager.sender == self.context.get("user", None)
            else wager.recipient
        )
        return opp.id

    def get_is_sender(self, wager):
        return wager.sender == self.context.get("user")

    def get_status(self, wager):
        return wager.status.split(".")[-1]


class WagerCreateSerializer(serializers.ModelSerializer):
    amount = MoneyField(max_digits=10, decimal_places=2)

    class Meta:
        model = Wager
        fields = ("game", "outcome", "recipient", "amount")

    def validate(self, data):
        if self.context.get("user") == data["recipient"]:
            raise serializers.ValidationError("You cannot send a wager to yourself.")

        if self.context.get("user").wallet.balance < Money(data["amount"], "USD"):
            raise serializers.ValidationError(
                "You don't have enough money for this transaction."
            )

        if data["outcome"] not in data["game"].outcomes.all():
            raise serializers.ValidationError(
                "This outcome is not a part of this game."
            )

        return data

    def create(self, data):
        amount = Money(data.get("amount"), "USD")
        if amount < Money(0, "USD"):
            raise ParseError(detail="Amount must not be negative.")
        data["sender"] = self.context.get("user")
        data["amount"] = amount
        return Wager.objects.create_wager(**data)
