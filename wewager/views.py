import pytz
from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, views, mixins
from rest_framework.response import Response
from .serializers import *


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    pass


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /user
    /user/:id
    Read-only viewset for users
    """

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class WalletViewSet(views.APIView):
    """
    /wallet
    Read-only view for user's wallet
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = WalletSerializer(request.user.wallet)
        return Response(serializer.data)


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /game
    /game/:id
    Returns games currently in progress or in the future
    """

    queryset = Game.objects.filter(date__gte=datetime.utcnow().replace(tzinfo=pytz.utc))
    serializer_class = GameSerializer


class WagerViewSet(CreateListRetrieveViewSet):
    """
    /wager
    /wager/:id
    List, create, and retrieve your wagers
    """

    serializer_class = WagerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wager.objects.filter(sender=self.request.user) | Wager.objects.filter(
            recipient=self.request.user
        )

    def get_serializer_context(self):
        return {"user": self.request.user}
