from rest_framework import serializers

from main.models import ProjectAccess


class ProjectAccessSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectAccess
        fields = [
            'id',
            'user',
            'project',
            'can_edit',
        ]
