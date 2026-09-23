from django.urls import path
from .views import song_list, create_activity

urlpatterns = [
    path("", song_list),
    path("activity/", create_activity),
]