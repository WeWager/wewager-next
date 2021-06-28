from wewager.serializers.wager import WagerSerializer
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User


class UserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@wewager.io", password="top_secret"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_user_list(self):
        response = self.client.get("/api/v1/social/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_user(self):
        response = self.client.get(
            f"/api/v1/social/user/{self.user.id}/", format="json"
        )
        expected_fields = ["avatar", "first_name", "last_name", "username"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue((x in response.data for x in expected_fields))

    def test_get_user_wallet(self):
        response = self.client.get(f"/api/v1/wallet/{self.user.id}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        balance = str(self.user.wallet.balance).lstrip("$").replace(",", "")
        self.assertEqual(response.data["balance"], balance)
