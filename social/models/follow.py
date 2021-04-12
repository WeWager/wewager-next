from django.db import models
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    is_following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    def __str__(self):
        return f"{self.follower.username} -> {self.is_following.username}"
