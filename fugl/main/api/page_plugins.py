from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import PagePlugin
from main.models import Project
from main.serializers import PagePluginSerializer
from main.util import UserAccess


class PagePluginViewSet(viewsets.GenericViewSet):

    queryset = PagePlugin.objects.all()
    project_queryset = Project.objects.all()
    serializer_class = PagePluginSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        if 'project' not in request.query_params:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        proj_id = request.query_params['project']
        project = get_object_or_404(self.project_queryset, pk=proj_id)

        if UserAccess(request.user).can_view(project):
            plugins = self.queryset.filter(project=project)
            serializer = self.serializer_class(plugins, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        if 'project' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        proj_id = request.data['project']
        project = get_object_or_404(self.project_queryset, pk=proj_id)

        if UserAccess(request.user).can_edit(project):
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
        plugin = get_object_or_404(self.queryset, pk=pk)
        if UserAccess(request.user).can_view(plugin.project):
            serializer = self.serializer_class(plugin)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @list_route(methods=['get'])
    def available(self, request):
        if request.method != 'GET':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        params = request.query_params
        if 'project' not in params or 'title' not in params:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        proj_id = params['project']
        project = get_object_or_404(self.project_queryset, pk=proj_id)
        if not UserAccess(request.user).can_view(project):
            return Response(status=status.HTTP_404_NOT_FOUND)
        constrained_queryset = self.queryset.filter(project=project)

        title = params['title']
        available = not constrained_queryset.filter(title=title).exists()
        resp_data = {'available': available}
        return Response(resp_data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        plugin = get_object_or_404(self.queryset, pk=pk)
        request.data.pop('project', None)

        if UserAccess(request.user).can_edit(plugin.project):
            serializer = self.serializer_class(plugin, data=request.data,
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
        plugin = get_object_or_404(self.queryset, pk=pk)
        if UserAccess(request.user).can_edit(plugin.project):
            plugin.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
