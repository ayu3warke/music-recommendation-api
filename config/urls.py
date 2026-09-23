from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse


def hello(request):
    return JsonResponse({
        "message": "Hello from Music Recommendation API!"
    })


def health(request):
    return JsonResponse({
        "status": "healthy",
        "service": "music-recommendation-api"
    })


urlpatterns = [
    path("admin/", admin.site.urls),

    path("hello/", hello),
    path("health/", health),

    path("users/", include("user_profiles.urls")),
    path("recommendations/", include("recommendations.urls")),
    path("activity/", include("analytics_api.urls")),
    path("analytics/", include("analytics_api.urls")),
]
