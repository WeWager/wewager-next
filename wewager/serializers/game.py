from rest_framework import serializers

from wewager.models import Game
from wewager.serializers.team_data import TeamDataSerializer


class GameSerializer(serializers.ModelSerializer):
    team_data = TeamDataSerializer(many=True)

    class Meta:
        model = Game
        fields = ("id", "date", "winner", "data", "team_data")