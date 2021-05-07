from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from social.serializers import UserSerializer


class CurrentUserPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == "current_user":
            return request.user.is_authenticated
        return True


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /user
    /user/:id
    Read-only viewset for users
    """

    queryset = get_user_model().objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [CurrentUserPermission]

    @action(methods=["GET"], detail=False)
    def current_user(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)