from django.db import models


class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    mood = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Activity(models.Model):
    user = models.ForeignKey(
        "users.UserProfile",
        on_delete=models.CASCADE,
        related_name="activities"
    )

    activity_type = models.CharField(max_length=50)
    song = models.ForeignKey(
        Song,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.activity_type}"