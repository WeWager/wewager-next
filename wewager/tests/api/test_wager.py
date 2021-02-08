from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User

from wewager.models import Team, Game, Wallet


class UserTestCase(APITestCase):
    def setUp(self):
        self.me = get_user_model().objects.create_user(
            username="myname", email="myname@wewager.io", password="hunter42"
        )
        self.me.wallet.add_balance(Money(100, "USD"), TransactionType.DEPOSIT)
        self.you = get_user_model().objects.create_user(
            username="yourname", email="yourname@wewager.io", password="42hunter"
        )
        self.you.wallet.add_balance(Money(100, "USD"), TransactionType.DEPOSIT)

        self.home = Team.objects.create(city="Philadelphia", name="76ers", abbr="PHI")
        self.away = Team.objects.create(city="Toronto", name="Raptors", abbr="TOR")
        self.game = Game.objects.create(date=datetime.now(pytz.utc))
        self.game.add_team(self.home, -3.5, -140)
        self.game.add_team(self.away, 3.5, 150)

        self.client = APIClient()
        self.client.force_authenticate(user=self.me)

        team_data = next(x for x in self.game.team_data if x.team.abbr == "PHI")
        self.first_wager = Wager.objects.create_wager(
            game=self.game,
            team=team_data,
            sender=self.me,
            sender_side=WagerSide.WIN,
            recipient=self.you,
            amount=Money(10, "USD"),
        )

    def test_get_wager_list(self):
        response = self.client.get("/api/v1/wager/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_wager(self):
        response = self.client.get(f"/api/v1/wager/{self.first_wager.id}")
        self.assertEqual(resposne.status_code, status.HTTP_200_OK)
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
