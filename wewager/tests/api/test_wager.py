import pytz
from datetime import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User

from wewager.models import Team, Game, Wallet, TransactionType, Wager, WagerSide

from moneyed import Money


class UserTestCase(APITestCase):
    def setUp(self):
        self.me = User.objects.create_user(
            username="myname", email="myname@wewager.io", password="hunter42"
        )
        self.me.wallet.add_balance(Money(100, "USD"), TransactionType.DEPOSIT)
        self.me.wallet.save()
        self.you = User.objects.create_user(
            username="yourname", email="yourname@wewager.io", password="42hunter"
        )
        self.you.wallet.add_balance(Money(100, "USD"), TransactionType.DEPOSIT)
        self.you.wallet.save()

        self.home = Team.objects.create(city="Philadelphia", name="76ers", abbr="PHI")
        self.away = Team.objects.create(city="Toronto", name="Raptors", abbr="TOR")
        self.game = Game.objects.create(date=datetime.now(pytz.utc))
        self.game.add_team(self.home, -3.5, -140)
        self.game.add_team(self.away, 3.5, 150)

        self.client = APIClient()
        self.client.force_authenticate(user=self.me)

        self.team_data = next(x for x in self.game.team_data if x.team.abbr == "PHI")
        self.first_wager = Wager.objects.create_wager(
            game=self.game,
            team=self.team_data,
            sender=self.you,
            sender_side=WagerSide.WIN,
            recipient=self.me,
            amount=Money(10, "USD"),
        )

    def test_get_wager_list(self):
        response = self.client.get("/api/v1/wager/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_wager(self):
        response = self.client.get(f"/api/v1/wager/{self.first_wager.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_fields = (
            "id",
            "game",
            "team",
            "opponent",
            "is_sender",
            "sender_side",
            "amount",
            "status",
        )
        self.assertTrue((x in response.data for x in expected_fields))

    def test_accept_wager(self):
        response = self.client.post(f"/api/v1/wager/{self.first_wager.id}/accept/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "accepted")

    def test_decline_wager(self):
        response = self.client.post(f"/api/v1/wager/{self.first_wager.id}/decline/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "declined")

    def test_create_wager(self):
        payload = {
            "game": self.game.id,
            "team": self.team_data.id,
            "sender_side": "W",
            "recipient": self.you.id,
            "amount": 10,
        }
        response = self.client.post(f"/api/v1/wager/", data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_wager_negative_amount(self):
        payload = {
            "game": self.game.id,
            "team": self.team_data.id,
            "sender_side": "W",
            "recipient": self.you.id,
            "amount": -10,
        }
        response = self.client.post(f"/api/v1/wager/", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wager_unknown_user(self):
        payload = {
            "game": self.game.id,
            "team": self.team_data.id,
            "sender_side": "W",
            "recipient": 21,
            "amount": 10,
        }
        response = self.client.post(f"/api/v1/wager/", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wager_invalid_side(self):
        payload = {
            "game": self.game.id,
            "team": self.team_data.id,
            "sender_side": "A",
            "recipient": self.you.id,
            "amount": 10,
        }
        response = self.client.post(f"/api/v1/wager/", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 

    def test_create_wager_invalid_team(self):
        payload = {
            "game": self.game.id,
            "team": 32,
            "sender_side": "W",
            "recipient": self.you.id,
            "amount": 10,
        }
        response = self.client.post(f"/api/v1/wager/", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 

    def test_create_wager_invalid_game(self):
        payload = {
            "game": 64,
            "team": self.team_data.id,
            "sender_side": "W",
            "recipient": self.you.id,
            "amount": 10,
        }
        response = self.client.post(f"/api/v1/wager/", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wager_against_self(self):
        payload = {
            "game": self.game.id,
            "team": self.team_data.id,
            "sender_side": "W",
            "recipient": self.me.id,
            "amount": 10,
        }
        response = self.client.post(f"/api/v1/wager/", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)