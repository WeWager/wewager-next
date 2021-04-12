from django.db import models
from django.contrib.auth.models import User


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    date = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=300, blank=False)
    parent = models.ForeignKey(
        "Post", related_name="comments", on_delete=models.CASCADE
    )
