from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Project
from main.serializers import ProjectPermissionSerializer
from main.serializers import ProjectSerializer
from main.util import UserAccess


class ProjectViewSet(viewsets.GenericViewSet):

    queryset = Project.objects.all()
    serializer_class = ProjectPermissionSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        user = request.user
        projects = user.project_set.all() | user.shared_projects.all()
        serializer = self.serializer_class(
            projects,
            many=True,
            context={'user': user},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @list_route()
    def owned(self, request):
        user = request.user
        projects = user.project_set.all()
        serializer = self.serializer_class(
            projects,
            many=True,
            context={'user': user},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @list_route()
    def shared(self, request):
        user = request.user
        shared_projects = user.shared_projects.all()
        serializer = self.serializer_class(
            shared_projects,
            many=True,
            context={'user': user},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        if not UserAccess(request.user).can_view(project):
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        if not UserAccess(request.user).can_edit(project):
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(project, data=request.data,
                                           partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        pass
