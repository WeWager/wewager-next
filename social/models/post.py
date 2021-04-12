import uuid

from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    date = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=300, blank=False)

    liked_by = models.ManyToManyField(User, blank=True)

    replies = models.ManyToManyField("Comment", blank=True)

    def like(self, user):
        self.liked_by.add(user)
        self.save()

    def dislike(self, user):
        self.liked_by.remove(user)
        self.save()
