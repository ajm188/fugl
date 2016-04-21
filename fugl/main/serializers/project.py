from rest_framework import serializers

from main.models import Project
from main.util import UserAccess


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'description',
            'preview_url',
            'owner',
            'theme',
        ]
        extra_kwargs = {
            'preview_url': {'allow_blank': True, 'default': ''},
        }

class ProjectPermissionSerializer(ProjectSerializer):

    def to_representation(self, project):
        d = super().to_representation(project)
        try:
            user = self.context['user']
            user_proxy = UserAccess(user)
            if user_proxy.can_edit(project):
                d['can_edit'] = True
            else:
                d['can_edit'] = False
        except KeyError:
            pass

        return d


class ProjectDetailSerializer(ProjectSerializer):

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + [
            'post_set', 'page_set', 'category_set', 'tag_set',
        ]
