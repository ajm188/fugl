from django import db
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Project
from main.models import ProjectAccess
from main.models import User
from main.serializers import ProjectAccessSerializer
from main.serializers import ProjectDetailSerializer
from main.serializers import ProjectPermissionSerializer
from main.serializers import ProjectSerializer
from main.serializers import UserSerializer
from main.util import UserAccess


class ProjectViewSet(viewsets.GenericViewSet):

    queryset = Project.objects.all()
    user_queryset = User.objects.all()
    serializer_class = ProjectPermissionSerializer
    retrieve_serializer_class = ProjectDetailSerializer
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

    def create(self, request):
        request.data['owner'] = request.user.id
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

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

    @list_route(methods=['get'])
    def lookup(self, request):
        if request.method != 'GET':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        params = request.query_params
        if 'username' not in params or 'title' not in params:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(self.user_queryset,
            username=params['username'])
        user_projects = self.queryset.filter(owner=user)
        project = get_object_or_404(user_projects, title=params['title'])
        if UserAccess(request.user).can_view(project):
            serializer = self.retrieve_serializer_class(project)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @list_route(methods=['get'])
    def available(self, request):
        user = request.user
        if 'title' not in request.query_params:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        title = request.query_params['title']
        available = not self.queryset.filter(owner=user, title=title).exists()
        resp = {'available': available}
        return Response(resp, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        if not UserAccess(request.user).can_view(project):
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.retrieve_serializer_class(project)
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

    @detail_route(methods=['post'])
    def clone(self, request, pk=None):
        project = get_object_or_404(self.queryset, pk=pk)

        if request.method != 'POST':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if project.owner != request.user:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = request.data
        if 'title' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        title = data['title']
        get_false = lambda key: data.get(key, False)
        clone_theme = get_false('theme')
        clone_pages = get_false('pages')
        clone_posts = get_false('posts')
        clone_plugins = get_false('plugins')
        with db.transaction.atomic():
            try:
                cloned_project = project.clone(
                    title,
                    clone_theme,
                    clone_pages,
                    clone_posts,
                    clone_plugins,
                )
            except db.utils.IntegrityError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(cloned_project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
