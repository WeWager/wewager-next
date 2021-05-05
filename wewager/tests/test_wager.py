from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase
from model_bakery import baker
from moneyed import Money
from parameterized import parameterized

from wewager.models import Wallet, TransactionType, Wager


WAGER_LIST = reverse("wager-list")


class WagerTests(APITransactionTestCase):
    def setUp(self):
        self.game = baker.make_recipe("wewager.game_with_outcomes")
        self.me = baker.make_recipe("wewager.user_recipe")
        Wallet.add_balance(self.me, Money(50, "USD"), TransactionType.DEPOSIT)
        self.me.refresh_from_db()
        self.you = baker.make_recipe("wewager.user_recipe")
        Wallet.add_balance(self.you, Money(50, "USD"), TransactionType.DEPOSIT)
        self.you.refresh_from_db()
        self.client.force_authenticate(user=self.me)

    def build_payload(self, **kwargs):
        return {
            "game": kwargs.get("game", self.game.id),
            "outcome": kwargs.get("outcome", self.game.outcomes.first().id),
            "recipient": kwargs.get("recipient", self.you.id),
            "amount": kwargs.get("amount", "10.00"),
        }

    def test_get_games(self):
        resp = self.client.get(reverse("game-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    @parameterized.expand([(x,) for x in range(4)])
    def test_create_wager(self, outcome_num):
        outcome_id = self.game.outcomes.all()[outcome_num].id
        resp = self.client.post(WAGER_LIST, self.build_payload(outcome=outcome_id))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Wager.objects.all().count(), 1)

    @parameterized.expand(
        [
            ("game", -1),
            ("game", ""),
            ("outcome", -1),
            ("outcome", ""),
            ("recipient", -1),
            ("recipient", ""),
            ("amount", "-10"),
            ("amount", "100"),
            ("amount", ""),
        ]
    )
    def test_create_wager_invalid(self, key, value):
        payload = self.build_payload(**{key: value})
        resp = self.client.post(WAGER_LIST, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @parameterized.expand(["game", "outcome", "recipient", "amount"])
    def test_create_wager_without_value(self, key):
        payload = self.build_payload()
        payload.pop(key)
        resp = self.client.post(WAGER_LIST, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wager_without_payload(self):
        resp = self.client.post(WAGER_LIST, {})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_wager_to_self(self):
        payload = self.build_payload(recipient=self.me.id)
        resp = self.client.post(WAGER_LIST, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
