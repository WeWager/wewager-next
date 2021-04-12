import pytz
from datetime import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from wewager.models import Game, Team


class GameTestCase(APITestCase):
    def setUp(self):
        self.home = Team.objects.create(city="Philadelphia", name="76ers", abbr="PHI")
        self.away = Team.objects.create(city="Toronto", name="Raptors", abbr="TOR")
        self.other = Team.objects.create(city="Boston", name="Celtics", abbr="BOS")
        self.game = Game.objects.create(date=datetime.now(pytz.utc))

    def test_get_game_list(self):
        response = self.client.get("/api/v1/game/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_game(self):
        response = self.client.get(f"/api/v1/game/{self.game.id}/", format="json")
        expected_fields = ["id", "date", "winner", "data", "team_data"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue((x in response.data for x in expected_fields))
