from django.test import TestCase
from rest_framework.test import APIClient

from users.models import UserProfile
from .models import Song


class MusicAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserProfile.objects.create(
            name="Test User",
            email="test@example.com",
            favorite_genres=["pop", "rock"],
            favorite_artists=["Ed Sheeran"],
            moods=["happy", "romantic"],
        )

        Song.objects.create(
            title="Perfect",
            artist="Ed Sheeran",
            genre="pop",
            mood="romantic",
        )

        Song.objects.create(
            title="Shape of You",
            artist="Ed Sheeran",
            genre="pop",
            mood="happy",
        )

        Song.objects.create(
            title="Believer",
            artist="Imagine Dragons",
            genre="rock",
            mood="energetic",
        )

    def test_get_songs(self):
        response = self.client.get("/songs/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_create_song(self):
        data = {
            "title": "Tum Hi Ho",
            "artist": "Arijit Singh",
            "genre": "bollywood",
            "mood": "romantic",
        }

        response = self.client.post(
            "/songs/",
            data,
            format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Tum Hi Ho")

    def test_recommendations(self):
        response = self.client.get(
            f"/recommendations/{self.user.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)

        # Highest scoring song should be first
        # Both Perfect and Shape of You should have the highest score
        self.assertEqual(response.data[0]["score"], 8)

        titles = [song["title"] for song in response.data]

        self.assertIn("Perfect", titles)
        self.assertIn("Shape of You", titles)

    def test_recommendation_limit(self):
        response = self.client.get(
            f"/recommendations/{self.user.id}/?limit=1"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_invalid_limit(self):
        response = self.client.get(
            f"/recommendations/{self.user.id}/?limit=abc"
        )

        self.assertEqual(response.status_code, 400)

    def test_zero_limit(self):
        response = self.client.get(
            f"/recommendations/{self.user.id}/?limit=0"
        )

        self.assertEqual(response.status_code, 400)

    def test_recommendations_user_not_found(self):
        response = self.client.get("/recommendations/999/")

        self.assertEqual(response.status_code, 404)