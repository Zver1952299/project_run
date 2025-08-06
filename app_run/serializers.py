from rest_framework import serializers
from app_run.models import Run
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type']

    def get_type(self, obj):
        return f"{'coach' if obj.is_staff else 'athlete'}"


class UserForRunsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserForRunsSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = '__all__'