from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q, OuterRef, Exists

from social.models import Post
from common.mixins import SearchActionMixin
from social.serializers import PostSerializer, CommentSerializer
from common.permissions import IsOwnerOrReadOnly, CanReactToPost


class PostViewSet(ModelViewSet, SearchActionMixin):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, (IsOwnerOrReadOnly | CanReactToPost)]
    search_fields = ["content"]

    def get_queryset(self):
        user = self.request.user
        liked = Post.objects.filter(id=OuterRef("id"), liked_by=user)
        return (
            Post.objects.all()
            .annotate(
                like_count=Count("liked_by"),
                reply_count=Count("comments"),
                liked=Exists(liked),
            )
            .order_by("-date")
        )

    def get_serializer_context(self):
        return {"user": self.request.user}

    def action_response(self, post):
        serializer = self.serializer_class(post)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def like(self, request, pk=None):
        post = self.get_object()
        post.like(self.request.user)
        return self.action_response(post)

    @action(detail=True, methods=["POST"])
    def dislike(self, request, pk=None):
        post = self.get_object()
        post.dislike(self.request.user)
        return self.action_response(post)

    @action(detail=True, methods=["GET"])
    def comment(self, request, pk=None):
        post = self.get_object()
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.paginate_queryset(comments, request)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=["POST"])
    def add_comment(self, request, pk=None):
        post = self.get_object()
        context = {"parent": post, "request": request}
        serializer = CommentSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            comment = serializer.save(user=self.request.user)
            return self.action_response(serializer.data)
