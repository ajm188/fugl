from rest_framework import serializers

from main.models import ProjectPlugin


class ProjectPluginSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectPlugin
        fields = ['id', 'title', 'markup', 'project']
