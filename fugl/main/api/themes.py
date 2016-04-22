from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Theme
from main.serializers import ThemeSerializer


class ThemeViewSet(viewsets.GenericViewSet):

    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        request.data['creator'] = request.user.id
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        theme = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(theme)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        theme = get_object_or_404(self.queryset, pk=pk)
        if theme.creator == request.user:
            serializer = self.serializer_class(theme, data=request.data,
                partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None):
        theme = get_object_or_404(self.queryset, pk=pk)
        if theme.creator == request.user:
            theme.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
