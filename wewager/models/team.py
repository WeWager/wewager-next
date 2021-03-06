from django.db import models


class Team(models.Model):
    city = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    abbr = models.CharField(max_length=5)
    teamUid = models.CharField(max_length=7)

    @property
    def full_name(self):
        return self.city + " " + self.name

    def __str__(self):
        return f"{self.city} {self.name}"
