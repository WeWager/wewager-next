from rest_framework import serializers

from wewager.models import Game, GameOutcome
from wewager.serializers.game_outcome import GameOutcomeSerializer


class GameSerializer(serializers.ModelSerializer):
    outcomes = GameOutcomeSerializer(many=True)

    class Meta:
        model = Game
        fields = ("id", "description", "date", "league", "ended", "data", "outcomes")
