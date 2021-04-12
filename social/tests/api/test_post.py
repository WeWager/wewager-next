from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User

from social.models import Post, Follow
from social.serializers import PostSerializer


class UserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@wewager.io", password="top_secret"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.other_user = User.objects.create_user(
            username="testuser2", email="test2@wewager.io", password="not_a_secret"
        )

        Follow.objects.create(follower=self.user, is_following=self.other_user)

    def create_own_post(self):
        return Post.objects.create(user=self.user, content="Hello, world!")

    def create_other_user_post(self):
        return Post.objects.create(user=self.other_user, content="Hi!")

    def test_get_posts_empty(self):
        response = self.client.get("/api/v1/social/post/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_get_posts_own(self):
        self.create_own_post()
        response = self.client.get("/api/v1/social/post/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
