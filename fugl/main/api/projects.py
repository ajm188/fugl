from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Project
from main.models import ProjectAccess
from main.serializers import ProjectAccessSerializer
from main.serializers import ProjectPermissionSerializer
from main.serializers import ProjectSerializer
from main.serializers import UserSerializer
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
        project = get_object_or_404(Project, pk=pk)
        if not project.owner_id == request.user.id:
            return Response(status=status.HTTP_404_NOT_FOUND)

        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['get', 'post', 'put', 'patch', 'delete'])
    def access(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)

        if request.method == 'GET':
            return self.get_project_access(request, project)
        elif request.method == 'POST':
            return self.create_project_access(request, project)
        elif request.method in ['PUT', 'PATCH']:
            return self.update_project_access(request, project)
        elif request.method == 'DELETE':
            return self.delete_project_access(request, project)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_project_access(self, request, project):
        if not UserAccess(request.user).can_view(project):
            return Response(status=status.HTTP_404_NOT_FOUND)

        accesses = project.projectaccess_set.all()
        serializer = ProjectAccessSerializer(accesses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_project_access(self, request, project):
        if not self.project_owner(request, project):
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = request.data
        if 'user' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_id = data['user']
        accesses = ProjectAccess.objects.filter(user_id=user_id,
            project=project)
        if accesses.exists():
            serializer = ProjectAccessSerializer(accesses[0])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            request.data.update({'project': project.id})
            serializer = ProjectAccessSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                    status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

    def update_project_access(self, request, project):
        if not self.project_owner(request, project):
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = request.data
        if 'user' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = data['user']
        access = get_object_or_404(
            ProjectAccess,
            project=project,
            user=user,
        )
        data.pop('project', None)  # don't let the user change the project
        serializer = ProjectAccessSerializer(
            access,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

    def delete_project_access(self, request, project):
        if not self.project_owner(request, project):
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = request.data
        if 'user' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = data['user']
        access = get_object_or_404(
            ProjectAccess,
            project=project,
            user=user,
        )
        access.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def project_owner(self, request, project):
        return project.owner_id == request.user.id
