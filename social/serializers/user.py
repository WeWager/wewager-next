from django.contrib.auth import get_user_model
from rest_framework import serializers


DEFAULT_AVATAR = "https://wewager-next.us-east-1.linodeobjects.com/avatars/default.png"


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    is_following = serializers.BooleanField(read_only=True, default=False)
    is_follower = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "avatar_url",
            "is_following",
            "is_follower"
        )

    def get_avatar_url(self, user):
        if hasattr(user, "avatar") and user.avatar.image:
            return user.avatar.image.url
        return DEFAULT_AVATAR


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "password", "email", "first_name", "last_name")
        read_only_fields = ["id"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, data):
        return get_user_model().objects.create_user(**data)
