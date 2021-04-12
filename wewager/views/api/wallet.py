from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from wewager.models import Wallet
from wewager.serializers import WalletSerializer


class WalletViewSet(ReadOnlyModelViewSet):
    """
    /wallet
    Read-only view for users' wallet
    """

    queryset = Wallet.objects.all().order_by("-balance")
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
