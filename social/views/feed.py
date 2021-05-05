from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, OuterRef, Exists

from social.models import Post
from .post_mixin import PostMixins
from social.serializers import PostSerializer


class FeedViewSet(viewsets.ModelViewSet, PostMixins):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        liked = Post.objects.filter(id=OuterRef("id"), liked_by=user)
        return (
            Post.objects.filter(Q(user=user) | Q(user__followers__follower=user))
            .annotate(
                like_count=Count("liked_by"),
                reply_count=Count("comments"),
                liked=Exists(liked),
            )
            .order_by("-date")
        )