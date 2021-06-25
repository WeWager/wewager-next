from rest_framework import serializers

from wewager.models import Wallet
from social.serializers.user import UserSerializer


class WalletSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Wallet
        fields = (
            "user",
            "balance",
        )
