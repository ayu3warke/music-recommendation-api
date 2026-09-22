from django.urls import path
from .views import song_list

urlpatterns = [
    path("", song_list),
]