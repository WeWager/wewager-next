import pytz
from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, views, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from .serializers import *


class ReadWriteSerializerMixin(object):
    """
    Overrides get_serializer_class to choose the read serializer
    for GET requests and the write serializer for POST requests.

    Set read_serializer_class and write_serializer_class attributes on a
    viewset.
    """

    read_serializer_class = None
    write_serializer_class = None

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return self.get_write_serializer_class()
        return self.get_read_serializer_class()

    def get_read_serializer_class(self):
        assert self.read_serializer_class is not None, (
            "'%s' should either include a `read_serializer_class` attribute,"
            "or override the `get_read_serializer_class()` method."
            % self.__class__.__name__
        )
        return self.read_serializer_class

    def get_write_serializer_class(self):
        assert self.write_serializer_class is not None, (
            "'%s' should either include a `write_serializer_class` attribute,"
            "or override the `get_write_serializer_class()` method."
            % self.__class__.__name__
        )
        return self.write_serializer_class


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


class WagerViewSet(ReadWriteSerializerMixin, CreateListRetrieveViewSet):
    """
    /wager
    /wager/:id
    List, create, and retrieve your wagers
    """

    read_serializer_class = WagerSerializer
    write_serializer_class = WagerCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wager.objects.filter(sender=self.request.user) | Wager.objects.filter(
            recipient=self.request.user
        )

    def get_serializer_context(self):
        return {"user": self.request.user}

    @action(detail=True, methods=["POST"])
    def accept(self, request, pk=None):
        wager = self.get_object()
        if request.user != wager.recipient:
            raise ParseError("You must be the recipient to accept a wager.")
        wager.accept()
        wager.save()
        serializer = WagerSerializer(wager)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def decline(self, request, pk=None):
        wager = self.get_object()
        if request.user != wager.recipient:
            raise ParseError("You must be the recipient to accept a wager.")
        wager.decline()
        wager.save()
        serializer = WagerSerializer(wager)
        return Response(serializer.data)
