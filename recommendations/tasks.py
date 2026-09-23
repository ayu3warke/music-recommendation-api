from celery import shared_task

from user_profiles.models import UserProfile
from .services import refresh_user_recommendations


@shared_task
def refresh_recommendations_task(user_id):
    user = UserProfile.objects.get(id=user_id)

    recommendation = refresh_user_recommendations(user)

    return {
        "user_id": user.id,
        "recommendation_id": recommendation.id,
        "source": recommendation.source,
    }


@shared_task
def refresh_all_recommendations():
    user_ids = list(
        UserProfile.objects.values_list("id", flat=True)
    )

    for user_id in user_ids:
        refresh_recommendations_task.delay(user_id)

    return {
        "users_queued": len(user_ids)
    }
