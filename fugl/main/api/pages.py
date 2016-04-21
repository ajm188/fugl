from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Page
from main.models import Project
from main.serializers import PageSerializer
from main.util import UserAccess


class PageViewSet(viewsets.GenericViewSet):

    queryset = Page.objects.all()
    project_queryset = Project.objects.all()
    serializer_class = PageSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        if 'project' not in request.query_params:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        proj_id = request.query_params['project']
        project = get_object_or_404(self.project_queryset, pk=proj_id)

        if UserAccess(request.user).can_view(project):
            pages = self.queryset.filter(project=project)
            serializer = self.serializer_class(pages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        if 'project' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(self.project_queryset,
            pk=request.data['project'])
        access = UserAccess(request.user)
        if access.can_edit(project):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                    status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        page = get_object_or_404(self.queryset, pk=pk)
        access = UserAccess(request.user)
        if access.can_view(page.project):
            serializer = self.serializer_class(page)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        page = get_object_or_404(self.queryset, pk=pk)
        access = UserAccess(request.user)
        request.data.pop('project', None)  # not allowed to change project
        if access.can_edit(page.project):
            serializer = self.serializer_class(page, data=request.data,
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
        page = get_object_or_404(self.queryset, pk=pk)
        access = UserAccess(request.user)
        if access.can_edit(page.project):
            page.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
