from rest_framework import serializers

from main.models import PagePlugin


class PagePluginSerializer(serializers.ModelSerializer):

    class Meta:
        model = PagePlugin
        fields = ['id', 'title', 'head_markup', 'body_markup', 'project']
