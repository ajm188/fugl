from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Project
from main.serializers import ProjectPermissionSerializer
from main.serializers import ProjectSerializer


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
        pass

    def update(self, request, pk=None):
        pass

    def delete(self, request, pk=None):
        pass
