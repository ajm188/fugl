from rest_framework import serializers

from main.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password',)
        extra_kwargs = {'password': {'write_only': True},}
