from django.db.models.expressions import Exists, OuterRef
from social.models.follow import Follow
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, AllowAny, IsAuthenticated
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

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = ("username", "first_name", "last_name")

    def get_queryset(self):
        return (
            get_user_model()
            .objects.all()
            .order_by("id")
            .select_related("avatar")
            .annotate(
                is_following=Exists(
                    Follow.objects.filter(
                        follower=self.request.user, is_following__id=OuterRef("id")
                    )
                ),
                is_follower=Exists(
                    Follow.objects.filter(
                        follower__id=OuterRef("id"), is_following=self.request.user
                    )
                ),
            )
        )

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
