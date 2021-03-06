from rest_framework import serializers

from wewager.models import TeamData
from wewager.serializers.team import TeamSerializer


class TeamDataSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = TeamData
        fields = ("id", "team", "spread", "moneyline")
