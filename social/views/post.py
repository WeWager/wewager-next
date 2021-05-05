from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from social.models import Post
from .post_mixin import PostMixins
from social.serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet, PostMixins):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.all()