from rest_framework import serializers

from main.models import Theme


class ThemeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Theme
        fields = [
            'id', 'title', 'filepath', 'body_markup', 'creator',
        ]
        extra_kwargs = {
            'filepath': {'allow_blank': True},
        }
