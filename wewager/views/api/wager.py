from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema, no_body

from wewager.models import Wager
from wewager.serializers import WagerSerializer, WagerCreateSerializer, EmptySerializer
from common.mixins import ReadWriteSerializerMixin
from common.viewsets import CreateListRetrieveViewSet


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
