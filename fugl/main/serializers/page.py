from rest_framework import serializers

from main.models import Page


class PageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Page
        fields = ['id', 'title', 'content', 'project']
