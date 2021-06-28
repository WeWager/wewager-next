from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.response import Response

from common.viewsets import CreateViewSet
from common.mixins import SearchActionMixin
from social.serializers import UserSerializer, UserCreateSerializer


class CurrentUserPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == "current_user":
            return request.user.is_authenticated
        return True


class UserViewSet(viewsets.ReadOnlyModelViewSet, SearchActionMixin):
    """
    /user
    /user/:id
    Read-only viewset for users
    """

    queryset = get_user_model().objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = (CurrentUserPermission,)
    search_fields = ("username", "first_name", "last_name")

    @action(methods=["GET"], detail=False)
    def current_user(self, request: Request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserRegistrationViewSet(CreateViewSet):
    """
    Create-only class for user registration
    """

    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
