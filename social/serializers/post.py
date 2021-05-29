from rest_framework import serializers

from social.models import Post
from social.serializers.user import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(read_only=True, default=0)
    reply_count = serializers.IntegerField(read_only=True, default=0)
    liked = serializers.BooleanField(read_only=True, default=False)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "user", "date", "content", "like_count", "reply_count", "liked")

    def create(self, data):
        data["user"] = self.context.get("user")
        return Post.objects.create(**data)
