from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from main.models import User
from main.serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    RO ModelViewSet provides:
        GET /users
        GET /users/<pk>
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        """
        User registration.

        POST /users
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
