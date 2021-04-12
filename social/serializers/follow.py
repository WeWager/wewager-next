from rest_framework import serializers

from social.models import Follow


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ("follower", "is_following")

    def validate(self, data):
        if data["follower"] != self.context.get("user"):
            raise serializers.ValidationError("You can only follow as yourself.")
        if data["follower"] == data["is_following"]:
            raise serializers.ValidationError("You can't follow yourself.")

    def create(self, validated_data):
        return Follow.objects.get_or_create(**validated_data)
