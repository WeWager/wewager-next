from rest_framework import serializers

from social.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    def create(self, validated_data):
        return Comment.objects.create(
            **validated_data, parent=self.context.get("parent")
        )

    class Meta:
        model = Comment
        fields = ("id", "user", "date", "content")
