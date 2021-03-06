from django.apps import apps
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Game(models.Model):
    date = models.DateTimeField()
    winner = models.ForeignKey("Team", null=True, blank=True, on_delete=models.CASCADE)
    gameUid = models.CharField(max_length=7)
    data = models.JSONField(null=True, blank=True)

    @property
    def teams(self):
        TeamData = apps.get_model("wewager", "TeamData")
        return [x.team for x in TeamData.objects.filter(game=self)]

    @property
    def team_data(self):
        TeamData = apps.get_model("wewager", "TeamData")
        return TeamData.objects.filter(game=self)

    @property
    def num_teams(self):
        TeamData = apps.get_model("wewager", "TeamData")
        return TeamData.objects.filter(game=self).count()

    @property
    def favorite(self):
        return min(self.team_data, key=lambda t: t.moneyline)

    @property
    def underdog(self):
        return max(self.team_data, key=lambda t: t.moneyline)

    def get_opponent(self, team):
        return next(x for x in self.team_data if x != team)

    @property
    def is_spread_covered(self):
        favorite = min(self.team_data, key=lambda t: t.spread)

    def add_team(self, team, spread, moneyline):
        TeamData = apps.get_model("wewager", "TeamData")
        return TeamData.objects.create(
            team=team, game=self, spread=spread, moneyline=moneyline
        )

    def set_winner(self, team):
        if team not in self.teams:
            return None
        self.winner = team

    def __str__(self):
        return f"<Game #{self.id}>"


@receiver(post_save, sender=Game)
def close_game(sender, **kwargs):
    Wager = apps.get_model("wewager", "Wager")
    instance = kwargs.get("instance", None)
    if instance is None:
        return
    if instance.winner is not None:
        assoc_wagers = Wager.objects.filter(game=instance)
        for wager in assoc_wagers:
            if wager.status == "pending":
                wager.expire()
            elif wager.status == "accepted":
                wager.complete()
            wager.save()
