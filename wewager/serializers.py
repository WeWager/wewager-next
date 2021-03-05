from .models import *
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from moneyed import Money
from djmoney.models.validators import MinMoneyValidator
from djmoney.contrib.django_rest_framework import MoneyField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_name", "last_name", "avatar")


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ("balance",)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("city", "name", "abbr")


class TeamDataSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = TeamData
        fields = ("id", "team", "spread", "moneyline")


class GameSerializer(serializers.ModelSerializer):
    team_data = TeamDataSerializer(many=True)

    class Meta:
        model = Game
        fields = ("id", "date", "winner", "data", "team_data")


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
            "team",
            "opponent",
            "is_sender",
            "sender_side",
            "amount",
            "recipient_amount",
            "status",
            "wager_type",
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
        fields = ("game", "team", "sender_side", "recipient", "amount", "wager_type")

    def create(self, data):
        amount = Money(data.get("amount"), "USD")
        if amount < Money(0, "USD"):
            raise ParseError(detail="Amount must not be negative.")
        data["sender"] = self.context.get("user")
        data["amount"] = amount
        return Wager.objects.create_wager(**data)
