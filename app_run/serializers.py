from rest_framework import serializers
from app_run.models import Run, AthleteInfo, Challenge
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

    # def get_runs_finished(self, obj):
    #     return obj.runs.filter(status=Run.Status.FINISHED).count()


class UserForRunsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class AthleteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AthleteInfo
        fields = ['goals', 'weight', 'user_id']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserForRunsSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = '__all__'


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['full_name', 'athlete']