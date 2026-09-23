from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from user_profiles.models import UserProfile
from .models import UserActivity


@api_view(["POST"])
def create_activity(request):
    user_id = request.data.get("user_id")
    track_id = request.data.get("track_id")
    action = request.data.get("action")

    if not user_id or not track_id or not action:
        return Response(
            {
                "error": "user_id, track_id and action are required"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if action not in ["play", "like", "skip"]:
        return Response(
            {
                "error": "action must be play, like or skip"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = get_object_or_404(UserProfile, id=user_id)

    activity = UserActivity.objects.create(
        user=user,
        track_id=track_id,
        track_name=request.data.get("track_name", ""),
        artist_name=request.data.get("artist_name", ""),
        genre=request.data.get("genre", ""),
        action=action,
    )

    return Response(
        {
            "message": "Activity recorded",
            "activity_id": activity.id,
            "user_id": user.id,
            "track_id": activity.track_id,
            "action": activity.action,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def analytics_summary(request):
    total_activities = UserActivity.objects.count()
    total_users = UserProfile.objects.count()

    action_counts = dict(
        UserActivity.objects
        .values("action")
        .annotate(count=Count("id"))
        .values_list("action", "count")
    )

    return Response({
        "total_users": total_users,
        "total_activities": total_activities,
        "plays": action_counts.get("play", 0),
        "likes": action_counts.get("like", 0),
        "skips": action_counts.get("skip", 0),
    })


@api_view(["GET"])
def analytics_trends(request):
    trends = (
        UserActivity.objects
        .annotate(date=TruncDate("created_at"))
        .values("date", "action")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    return Response({
        "trends": list(trends)
    })


@api_view(["GET"])
def user_analytics(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)

    activities = UserActivity.objects.filter(user=user)

    action_counts = dict(
        activities
        .values("action")
        .annotate(count=Count("id"))
        .values_list("action", "count")
    )

    top_tracks = list(
        activities
        .values("track_id", "track_name", "artist_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    return Response({
        "user_id": user.id,
        "user_name": user.name,
        "total_activities": activities.count(),
        "plays": action_counts.get("play", 0),
        "likes": action_counts.get("like", 0),
        "skips": action_counts.get("skip", 0),
        "top_tracks": top_tracks,
    })