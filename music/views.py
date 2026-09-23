import json

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Song, Activity
from user_profiles.models import UserProfile
from config.redis_client import redis_client
from .tasks import refresh_recommendations


@api_view(["GET", "POST"])
def song_list(request):

    if request.method == "GET":
        songs = Song.objects.all()

        data = [
            {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "genre": song.genre,
                "mood": song.mood,
            }
            for song in songs
        ]

        return Response(
            data,
            status=status.HTTP_200_OK
        )

    song = Song.objects.create(
        title=request.data.get("title"),
        artist=request.data.get("artist"),
        genre=request.data.get("genre"),
        mood=request.data.get("mood"),
    )

    return Response(
        {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
        },
        status=status.HTTP_201_CREATED
    )


@api_view(["GET"])
def recommendations(request, user_id):

    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    limit = request.query_params.get("limit")

    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return Response(
                {"error": "limit must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if limit <= 0:
            return Response(
                {"error": "limit must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST
            )

    if limit:
        cache_key = f"recommendations:{user_id}:limit:{limit}"
    else:
        cache_key = f"recommendations:{user_id}:all"

    cached_recommendations = redis_client.get(cache_key)

    if cached_recommendations:
        recommendations = json.loads(cached_recommendations)

        return Response(
            recommendations,
            status=status.HTTP_200_OK
        )

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

    if limit:
        recommendations = recommendations[:limit]

    redis_client.set(
        cache_key,
        json.dumps(recommendations),
        ex=300
    )

    return Response(
        recommendations,
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
def refresh_recommendations_api(request, user_id):

    try:
        UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    task = refresh_recommendations.delay(user_id)

    return Response(
        {
            "message": "Recommendation refresh started",
            "task_id": task.id,
            "user_id": user_id,
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(["POST"])
def create_activity(request):

    user_id = request.data.get("user_id")
    activity_type = request.data.get("activity_type")
    song_id = request.data.get("song_id")

    if not user_id:
        return Response(
            {"error": "user_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not activity_type:
        return Response(
            {"error": "activity_type is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    song = None

    if song_id:
        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return Response(
                {"error": "Song not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    activity = Activity.objects.create(
        user=user,
        activity_type=activity_type,
        song=song,
    )

    return Response(
        {
            "id": activity.id,
            "user_id": user.id,
            "activity_type": activity.activity_type,
            "song_id": activity.song.id if activity.song else None,
            "created_at": activity.created_at,
        },
        status=status.HTTP_201_CREATED
    )