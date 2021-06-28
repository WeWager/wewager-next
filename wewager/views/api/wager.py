from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
import django_filters.rest_framework as filters

from wewager.models import Wager
from wewager.serializers import WagerSerializer, EmptySerializer
from common.viewsets import CreateListRetrieveViewSet


class WagerViewSet(CreateListRetrieveViewSet):
    """
    List, create, and retrieve your wagers
    """

    serializer_class = WagerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ("game", "recipient", "status", "amount")

    def get_queryset(self):
        return Wager.objects.filter(sender=self.request.user) | Wager.objects.filter(
            recipient=self.request.user
        ).order_by("status")

    def get_serializer_context(self):
        return {"user": self.request.user}

    @swagger_auto_schema(method="post", request_body=EmptySerializer)
    @action(detail=True, methods=["POST"])
    def accept(self, request, pk=None):
        wager = self.get_object()
        if request.user != wager.recipient:
            raise ParseError("You must be the recipient to accept a wager.")
        wager.accept()
        wager.save()
        serializer = WagerSerializer(wager)
        return Response(serializer.data)

    @swagger_auto_schema(method="post", request_body=EmptySerializer)
    @action(detail=True, methods=["POST"])
    def decline(self, request, pk=None):
        wager = self.get_object()
        if request.user != wager.recipient:
            raise ParseError("You must be the recipient to accept a wager.")
        wager.decline()
        wager.save()
        serializer = WagerSerializer(wager)
        return Response(serializer.data)
