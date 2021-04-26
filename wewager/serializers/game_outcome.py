from rest_framework import serializers

from wewager.models import GameOutcome


class GameOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameOutcome
        fields = ("id", "description", "bet_type", "bet_price", "update_dt", "hit")
