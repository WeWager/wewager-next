from rest_framework import views, permissions
from rest_framework.response import Response

from wewager.serializers import WalletSerializer


class WalletViewSet(views.APIView):
    """
    /wallet
    Read-only view for user's wallet
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = WalletSerializer(request.user.wallet)
        return Response(serializer.data)