from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from social.serializers import CommentSerializer


class PostMixins:

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
