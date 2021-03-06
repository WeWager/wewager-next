from django.db import models

from wewager.models.game import Game
from wewager.models.team import Team


class TeamData(models.Model):
    description = models.CharField(max_length=45)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    spread = models.DecimalField(decimal_places=1, max_digits=3)
    moneyline = models.IntegerField()
    winning_position = models.IntegerField(default=1)
    end_position = models.IntegerField(null=True)

    def __str__(self):
        return f"<TeamData {self.team.abbr} {self.game.date}>"
