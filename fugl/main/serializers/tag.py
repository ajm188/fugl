from rest_framework import serializers

from main.models import Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'title', 'project', 'posts']
        read_only_fields = ['posts']
