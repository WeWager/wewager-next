from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from social.models import Follow
from social.serializers import FollowSerializer
from common.viewsets import ListCreateViewSet


class FollowViewSet(ListCreateViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        req_type = self.request.query_params.get("type", "following")
        return (
            Follow.objects.filter(follower=user)
            if req_type == "following"
            else Follow.objects.filter(is_following=user)
        )

    def get_serializer_context(self):
        return {"user": self.request.user}
