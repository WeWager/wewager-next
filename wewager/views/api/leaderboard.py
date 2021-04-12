from rest_framework import viewsets

from wewager.models import Wallet
from wewager.serializers import WalletSerializer


class LeaderboardViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all().order_by("-balance")
    serializer_class = WalletSerializer
