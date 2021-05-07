from rest_framework import serializers

from social.models import Post
from social.serializers.user import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    liked = serializers.BooleanField(read_only=True)
    user = UserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Post
        fields = ("id", "user", "date", "content", "like_count", "reply_count", "liked")
