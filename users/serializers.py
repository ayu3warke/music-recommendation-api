from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "name",
            "email",
            "favorite_genres",
            "favorite_artists",
            "moods",
            "created_at",
            "updated_at",
        ]