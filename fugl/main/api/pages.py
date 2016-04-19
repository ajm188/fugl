from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Page
from main.models import Project
from main.models import User
from main.serializers import PageSerializer
from main.util import UserAccess


class PageViewSet(viewsets.GenericViewSet):

    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        if 'project' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Project, pk=request.data['project'])
        access = UserAccess(request.user)
        if access.can_edit(project):
            pass
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        page = get_object_or_404(self.queryset, pk=pk)
        access = UserAccess(request.user)
        if access.can_view(page.project):
            serializer = PageSerializer(page)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        page = get_object_or_404(self.queryset, pk=pk)
        access = UserAccess(request.user)
        if access.can_edit(page.project):
            pass
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None):
        page = get_object_or_404(self.queryset, pk=pk)
        access = UserAccess(request.user)
        if access.can_edit(page.project):
            pass
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
