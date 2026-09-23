from django.db import models
from user_profiles.models import UserProfile


class UserActivity(models.Model):
    ACTION_CHOICES = [
        ("play", "Play"),
        ("like", "Like"),
        ("skip", "Skip"),
    ]

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    track_id = models.CharField(max_length=200)
    track_name = models.CharField(max_length=300, blank=True)
    artist_name = models.CharField(max_length=300, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.action} - {self.track_name}"
