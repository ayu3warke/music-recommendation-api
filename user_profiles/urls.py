from django.urls import path
from .views import create_or_update_user, user_detail

urlpatterns = [
    path("", create_or_update_user),
    path("<int:user_id>/", user_detail),
]
