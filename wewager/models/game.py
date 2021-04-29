from datetime import timedelta, datetime
from django.apps import apps
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class Game(models.Model):
    description = models.CharField(max_length=64)
    date = models.DateTimeField()
    date_eastern = models.DateTimeField(null=True)
    external_uid = models.CharField(max_length=64, unique=True)
    data = models.JSONField(null=True, blank=True)
    league = models.CharField(max_length=10)
    ended = models.BooleanField(default=False)
    outcomes = models.ManyToManyField("GameOutcome")

    class Meta:
        ordering = ("date",)

    @property
    def winner(self):
        if self.ended and self.data is not None:
            teams = self.data.get("participants")
            if teams:
                return max(teams, key=lambda x: x["score"])["name"]
        return None

    @property
    def time_eastern(self):
        return self.date - timedelta(hours=4)

    @property
    def status(self):
        if self.data:
            return self.data.get("status", None)
        return None

    @property
    def started(self):
        return self.date_eastern > datetime.today()

    def __str__(self):
        return f"[{self.league}] {self.description} {self.date}"


@receiver(pre_save, sender=Game)
def _set_eastern_time(sender, instance, **kwargs):
    instance.date_eastern = instance.date - timedelta(hours=5)
