import json

from celery import shared_task

from users.models import UserProfile
from .models import Song
from config.redis_client import redis_client


@shared_task
def refresh_recommendations(user_id):

    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        return {
            "success": False,
            "error": "User not found"
        }

    songs = Song.objects.all()

    recommendations = []

    for song in songs:

        score = 0
        reasons = []

        if song.genre in user.favorite_genres:
            score += 3
            reasons.append("favorite genre")

        if song.artist in user.favorite_artists:
            score += 3
            reasons.append("favorite artist")

        if song.mood in user.moods:
            score += 2
            reasons.append("matching mood")

        if score > 0:
            recommendations.append(
                {
                    "id": song.id,
                    "title": song.title,
                    "artist": song.artist,
                    "genre": song.genre,
                    "mood": song.mood,
                    "score": score,
                    "reason": reasons,
                }
            )

    recommendations.sort(
        key=lambda song: song["score"],
        reverse=True
    )

    # Refresh the main recommendation cache
    cache_key = f"recommendations:{user_id}:all"

    redis_client.set(
        cache_key,
        json.dumps(recommendations),
        ex=300
    )

    # Remove old limited-result caches
    for key in redis_client.scan_iter(
        match=f"recommendations:{user_id}:limit:*"
    ):
        redis_client.delete(key)

    return {
        "success": True,
        "user_id": user_id,
        "recommendations_count": len(recommendations)
    }