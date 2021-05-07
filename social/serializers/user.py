from django.contrib.auth import get_user_model
from rest_framework import serializers


DEFAULT_AVATAR = "https://wewager-next.us-east-1.linodeobjects.com/avatars/default.png"


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_name", "last_name", "avatar_url")

    def get_avatar_url(self, user):
        if hasattr(user, "avatar") and user.avatar.image:
            return user.avatar.image.url
        return DEFAULT_AVATAR
