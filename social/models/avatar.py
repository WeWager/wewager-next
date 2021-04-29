from django.contrib.auth import get_user_model
from django.db import models


class Avatar(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    image = models.ImageField(upload_to="avatars")
