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
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)

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
