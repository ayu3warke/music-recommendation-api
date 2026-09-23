from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import UserProfile


@api_view(["POST"])
def create_or_update_user(request):
    name = request.data.get("name")
    email = request.data.get("email")

    if not name or not email:
        return Response(
            {"error": "name and email are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = {
        "name": name,
        "email": email,
        "favorite_genres": request.data.get("favorite_genres", []),
        "favorite_artists": request.data.get("favorite_artists", []),
        "moods": request.data.get("moods", []),
    }

    user = UserProfile.objects.filter(email=email).first()

    if user:
        for field, value in data.items():
            setattr(user, field, value)

        user.save()

        return Response(
            {
                "message": "User profile updated",
                "user_id": user.id,
                **data,
            },
            status=status.HTTP_200_OK,
        )

    user = UserProfile.objects.create(**data)

    return Response(
        {
            "message": "User profile created",
            "user_id": user.id,
            **data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def user_detail(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)

    return Response({
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "favorite_genres": user.favorite_genres,
        "favorite_artists": user.favorite_artists,
        "moods": user.moods,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    })
