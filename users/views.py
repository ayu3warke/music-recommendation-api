from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import UserProfile
from .serializers import UserProfileSerializer


@api_view(["GET", "POST"])
def create_user(request):

    if request.method == "GET":
        users = UserProfile.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    serializer = UserProfileSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response(
            UserProfileSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def user_detail(request, pk):

    try:
        user = UserProfile.objects.get(pk=pk)
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = UserProfileSerializer(user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    if request.method in ["PUT", "PATCH"]:
        serializer = UserProfileSerializer(
            user,
            data=request.data,
            partial=(request.method == "PATCH")
        )

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserProfileSerializer(user).data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == "DELETE":
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)