from django.contrib.auth import get_user_model
from rest_framework import viewsets

from social.serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /user
    /user/:id
    Read-only viewset for users
    """

    queryset = get_user_model().objects.all().order_by("id")
    serializer_class = UserSerializer
