from django.core.cache import cache
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from user_profiles.models import UserProfile
from .tasks import refresh_recommendations_task
from .models import Recommendation


@api_view(["POST"])
def refresh_recommendations(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)

    task = refresh_recommendations_task.delay(user.id)

    return Response(
        {
            "message": "Recommendation refresh started",
            "user_id": user.id,
            "task_id": task.id,
        },
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(["GET"])
def get_recommendations(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)

    cache_key = f"recommendations:user:{user.id}"
    cached = cache.get(cache_key)

    if cached:
        return Response({
            "user_id": user.id,
            "cached": True,
            **cached,
        })

    latest = (
        Recommendation.objects
        .filter(user=user)
        .order_by("-created_at")
        .first()
    )

    if not latest:
        return Response(
            {
                "message": "No recommendations available. "
                "Call the refresh endpoint first."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    cache.set(
        cache_key,
        {
            "user_id": user.id,
            "source": latest.source,
            "tracks": latest.tracks,
            "recommendation_id": latest.id,
        },
        3600,
    )

    return Response({
        "user_id": user.id,
        "cached": False,
        "source": latest.source,
        "tracks": latest.tracks,
        "recommendation_id": latest.id,
    })
