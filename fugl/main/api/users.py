from django.contrib import auth

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import list_route
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

    @list_route()
    def available(self, request):
        """
        Check if a username is available.
        GET /users/available?username=<name>
        """
        username = request.query_params['username']
        resp_data = {}
        if User.objects.filter(username=username).exists():
            resp_data['available'] = False
        else:
            resp_data['available'] = True
        return Response(resp_data, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def authenticate(self, request):
        if request.method != 'POST':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        data = request.data
        if 'username' not in data or 'password' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        username = data['username']
        password = data['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
