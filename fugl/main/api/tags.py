from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Project
from main.models import Tag
from main.serializers import TagSerializer
from main.util import UserAccess


class TagViewSet(viewsets.GenericViewSet):

    queryset = Tag.objects.all()
    project_queryset = Project.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        if 'project' not in request.query_params:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        proj_id = request.query_params['project']
        project = get_object_or_404(self.project_queryset, pk=proj_id)

        if UserAccess(request.user).can_view(project):
            tags = self.queryset.filter(project=project)
            serializer = self.serializer_class(tags, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        if 'project' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Project, pk=request.data['project'])
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

    @list_route(methods=['get'])
    def available(self, request):
        params = request.query_params
        if 'project' not in params or 'title' not in params:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Project, pk=params['project'])
        if not UserAccess(request.user).can_edit(project):
            return Response(status=status.HTTP_404_NOT_FOUND)

        project_tags = self.queryset.filter(project=project)

        title = params['title']
        data = {
            'available': not project_tags.filter(title=title).exists(),
        }
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        tag = get_object_or_404(self.queryset, pk=pk)
        access = UserAccess(request.user)
        if access.can_view(tag.project):
            serializer = self.serializer_class(tag)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        tag = get_object_or_404(self.queryset, pk=pk)
        access = UserAccess(request.user)
        request.data.pop('project', None)  # not allowed to change project
        if access.can_edit(tag.project):
            serializer = self.serializer_class(tag, data=request.data,
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
        tag = get_object_or_404(self.queryset, pk=pk)
        access = UserAccess(request.user)
        if access.can_edit(tag.project):
            tag.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
