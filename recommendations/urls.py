from django.urls import path

from .views import (
    refresh_recommendations,
    get_recommendations,
)

urlpatterns = [
    path(
        "<int:user_id>/refresh/",
        refresh_recommendations,
    ),
    path(
        "<int:user_id>/",
        get_recommendations,
    ),
]
