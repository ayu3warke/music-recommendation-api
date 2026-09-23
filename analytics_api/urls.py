from django.urls import path

from .views import (
    create_activity,
    analytics_summary,
    analytics_trends,
    user_analytics,
)

urlpatterns = [
    path("", create_activity),
    path("summary/", analytics_summary),
    path("trends/", analytics_trends),
    path("user/<int:user_id>/", user_analytics),
]