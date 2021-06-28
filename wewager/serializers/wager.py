from django.contrib.auth.models import User
from djmoney.contrib.django_rest_framework import MoneyField
from moneyed import Money
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from wewager.models import Wager, Game, GameOutcome
from social.serializers import UserSerializer
from wewager.serializers.game import GameSerializer
from wewager.serializers.game_outcome import GameOutcomeSerializer


class WagerGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("id", "description", "date", "league", "ended", "status")


class WagerSerializer(serializers.ModelSerializer):
    opponent = serializers.SerializerMethodField()
    recipient = UserSerializer(read_only=True)
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="recipient", write_only=True
    )
    outcome = GameOutcomeSerializer(read_only=True)
    outcome_id = serializers.PrimaryKeyRelatedField(
        queryset=GameOutcome.objects.all(), source="outcome", write_only=True
    )
    game = WagerGameSerializer(read_only=True)
    game_id = serializers.PrimaryKeyRelatedField(
        queryset=Game.objects.all(), source="game", write_only=True
    )
    is_sender = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    amount = MoneyField(max_digits=10, decimal_places=2)
    recipient_amount = MoneyField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Wager
        depth = 1
        fields = (
            "id",
            "game",
            "game_id",
            "outcome",
            "outcome_id",
            "opponent",
            "is_sender",
            "recipient_amount",
            "amount",
            "status",
            "recipient",
            "recipient_id",
        )
        read_only_fields = (
            "game_desc",
            "is_sender",
            "status",
            "recipient",
            "outcome",
            "game",
        )

    def get_opponent(self, wager):
        opp = (
            wager.recipient
            if wager.sender == self.context.get("user", None)
            else wager.sender
        )
        return UserSerializer(opp).data

    def get_is_sender(self, wager):
        return wager.sender == self.context.get("user")

    def get_status(self, wager):
        return wager.status.split(".")[-1]

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
            raise serializers.ValidationError("Amount must not be negative.")
        data["sender"] = self.context.get("user")
        data["amount"] = amount
        return Wager.objects.create_wager(**data)
