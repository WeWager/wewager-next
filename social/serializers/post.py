from rest_framework import serializers

from social.models import Post


class PostSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "user", "date", "content", "like_count", "reply_count", "liked")
