from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import viewsets
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
