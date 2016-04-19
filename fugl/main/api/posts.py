from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Post
from main.models import Project
from main.serializers import PostSerializer
from main.util import UserAccess


class PostViewSet(viewsets.GenericViewSet):

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        if 'project' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Project, pk=request.data['project'])
        access = UserAccess(request.user)
        if access.can_edit(project):
            timestamp = timezone.now()
            request.data.update({
                'date_created': timestamp,
                'date_updated': timestamp,
            })
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
        post = get_object_or_404(self.queryset, pk=pk)
        access = UserAccess(request.user)
        if access.can_view(post.project):
            serializer = self.serializer_class(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        post = get_object_or_404(self.queryset, pk=pk)
        access = UserAccess(request.user)
        # Not allowed to change project or date_created
        # date_updated is managed automatically
        request.data.pop('project', None)
        request.data.pop('date_created', None)
        request.data.update({'date_updated': timezone.now()})
        if access.can_edit(post.project):
            serializer = self.serializer_class(post, data=request.data,
                partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
