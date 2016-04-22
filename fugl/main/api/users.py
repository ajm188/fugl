from django.contrib import auth
from django.shortcuts import get_object_or_404

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

    @list_route(methods=['get'])
    def lookup(self, request):
        if request.method != 'GET':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        params = request.query_params
        if 'username' not in params:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(self.queryset, username=params['username'])
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @list_route(methods=['delete'])
    def logout(self, request):
        if request.method != 'DELETE':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        auth.logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['get'])
    def session(self, request):
        """ Checks if a session is valid. """
        if request.method != 'GET':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        data = {'valid': request.user.is_authenticated()}
        return Response(data, status=status.HTTP_200_OK)
