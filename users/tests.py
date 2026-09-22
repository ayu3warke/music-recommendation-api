from django.test import TestCase
from rest_framework.test import APIClient

from .models import UserProfile


class UserAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "favorite_genres": ["pop", "rock"],
            "favorite_artists": ["Ed Sheeran"],
            "moods": ["happy", "romantic"],
        }

    def test_create_user(self):
        response = self.client.post(
            "/users/",
            self.user_data,
            format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Test User")

    def test_get_users(self):
        UserProfile.objects.create(**self.user_data)

        response = self.client.get("/users/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_user_detail(self):
        user = UserProfile.objects.create(**self.user_data)

        response = self.client.get(f"/users/{user.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test User")

    def test_user_not_found(self):
        response = self.client.get("/users/999/")

        self.assertEqual(response.status_code, 404)
