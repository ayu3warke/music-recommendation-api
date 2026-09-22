from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Song


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

        return Response(data, status=status.HTTP_200_OK)

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

from users.models import UserProfile


@api_view(["GET"])
def recommendations(request, user_id):

    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
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

        recommendations = recommendations[:limit]

    return Response(
        recommendations,
        status=status.HTTP_200_OK
    )