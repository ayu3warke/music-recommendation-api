from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from user_profiles.models import UserProfile
from recommendations.models import Recommendation
from analytics_api.models import UserActivity
from django.core.cache import cache


class MusicRecommendationAPITests(TestCase):
    def setUp(self):
        cache.clear()

        self.client = APIClient()

        self.user = UserProfile.objects.create(
            name="Test User",
            email="test@example.com",
            favorite_genres=["rock"],
            favorite_artists=["Coldplay"],
            moods=["happy"],
        )

    def test_create_user(self):
        response = self.client.post(
            "/users/",
            {
                "name": "New User",
                "email": "new@example.com",
                "favorite_genres": ["pop"],
                "favorite_artists": ["Taylor Swift"],
                "moods": ["happy"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "New User")

    def test_update_existing_user(self):
        response = self.client.post(
            "/users/",
            {
                "name": "Updated User",
                "email": self.user.email,
                "favorite_genres": ["jazz"],
                "favorite_artists": ["Miles Davis"],
                "moods": ["calm"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, "Updated User")
        self.assertEqual(self.user.favorite_genres, ["jazz"])

    def test_get_user(self):
        response = self.client.get(f"/users/{self.user.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertEqual(response.data["email"], self.user.email)

    @patch("recommendations.services.SpotifyClient.get_recommendations")
    def test_refresh_recommendations_with_spotify(self, mock_recommendations):
        mock_recommendations.return_value = [
            {
                "id": "track-1",
                "name": "Test Song",
                "artists": ["Test Artist"],
                "album": "Test Album",
                "spotify_url": "https://example.com",
                "preview_url": None,
                "duration_ms": 200000,
            }
        ]

        # Execute Celery task synchronously for the test.
        with patch(
            "recommendations.views.refresh_recommendations_task.delay"
        ) as mock_task:
            mock_task.return_value.id = "test-task-id"

            response = self.client.post(
                f"/recommendations/{self.user.id}/refresh/"
            )

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data["user_id"], self.user.id)
        mock_task.assert_called_once_with(self.user.id)

    def test_get_recommendations_when_missing(self):
        response = self.client.get(
            f"/recommendations/{self.user.id}/"
        )

        self.assertEqual(response.status_code, 404)

    def test_get_recommendations_after_creation(self):
        tracks = [
            {
                "id": "track-1",
                "name": "Test Song",
                "artists": ["Test Artist"],
                "album": "Test Album",
                "spotify_url": None,
                "preview_url": None,
                "duration_ms": 200000,
            }
        ]

        Recommendation.objects.create(
            user=self.user,
            tracks=tracks,
            source="demo",
        )

        response = self.client.get(
            f"/recommendations/{self.user.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertEqual(response.data["source"], "demo")
        self.assertEqual(response.data["tracks"], tracks)
        self.assertIn("recommendation_id", response.data)

    def test_recommendations_user_not_found(self):
        response = self.client.get("/recommendations/99999/")

        self.assertEqual(response.status_code, 404)

    def test_activity_creation(self):
        response = self.client.post(
            "/activity/",
            {
                "user_id": self.user.id,
                "track_id": "track-123",
                "action": "play",
                "track_name": "Test Song",
                "artist_name": "Test Artist",
                "genre": "rock",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertEqual(response.data["track_id"], "track-123")
        self.assertEqual(response.data["action"], "play")

        self.assertEqual(
            UserActivity.objects.filter(user=self.user).count(),
            1,
        )

    def test_activity_invalid_action(self):
        response = self.client.post(
            "/activity/",
            {
                "user_id": self.user.id,
                "track_id": "track-123",
                "action": "invalid",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_activity_missing_required_field(self):
        response = self.client.post(
            "/activity/",
            {
                "user_id": self.user.id,
                "track_id": "track-123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_activity_user_not_found(self):
        response = self.client.post(
            "/activity/",
            {
                "user_id": 99999,
                "track_id": "track-123",
                "action": "play",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_analytics_summary(self):
        UserActivity.objects.create(
            user=self.user,
            track_id="track-1",
            action="play",
        )

        UserActivity.objects.create(
            user=self.user,
            track_id="track-2",
            action="like",
        )

        response = self.client.get("/analytics/summary/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_users"], 1)
        self.assertEqual(response.data["total_activities"], 2)
        self.assertEqual(response.data["plays"], 1)
        self.assertEqual(response.data["likes"], 1)
        self.assertEqual(response.data["skips"], 0)

    def test_user_analytics(self):
        UserActivity.objects.create(
            user=self.user,
            track_id="track-1",
            track_name="Test Song",
            action="play",
        )

        response = self.client.get(
            f"/analytics/user/{self.user.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertEqual(response.data["total_activities"], 1)
        self.assertEqual(response.data["plays"], 1)

    def test_health_endpoint(self):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
