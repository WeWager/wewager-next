from rest_framework import serializers

from wewager.models import Team


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("city", "name", "abbr")