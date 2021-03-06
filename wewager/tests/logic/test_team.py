from datetime import datetime

import pytz
from django.test import TestCase

from wewager.models import Team, Game


class TeamTestCase(TestCase):
    def setUp(self):
        self.home = Team.objects.create(city="Philadelphia", name="76ers", abbr="PHI")
        self.away = Team.objects.create(city="Toronto", name="Raptors", abbr="TOR")
        self.other = Team.objects.create(city="Boston", name="Celtics", abbr="BOS")
        self.game = Game.objects.create(date=datetime.now(pytz.utc))

    def test_add_team_to_game(self):
        self.game.add_team(self.home, -2.5, -140)
        self.game.add_team(self.away, 2.5, 150)
        teams = self.game.teams
        assert self.home in teams
        assert self.away in teams
        assert len(teams) == 2

    def test_set_winner(self):
        assert self.game.winner == None
        self.game.add_team(self.home, -2.5, -140)
        self.game.add_team(self.away, 2.5, 150)
        self.game.set_winner(self.other)
        assert self.game.winner == None
        self.game.set_winner(self.home)
        assert self.game.winner == self.home