from rest_framework import serializers

from main.models import Post


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'project',
            'category',
            'date_created',
            'date_updated',
        ]
