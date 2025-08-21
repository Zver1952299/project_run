from django.contrib.auth.models import User
from django.db.models import Count, Q, Avg
from app_run.models import Run
from app_run.serializers import UserSerializer, UserForCoachSerializer, UserForAthleteSerializer


class UserService:
    @staticmethod
    def get_filtered_users(user_type=None):
        qs = User.objects.filter(is_superuser=False)
        qs = qs.annotate(
            runs_finished=Count(
                'runs',
                filter=Q(runs__status=Run.Status.FINISHED)
            ),
            rating=Avg('subscribers__rating')
        )
        if user_type == 'athlete':
            qs = qs.filter(is_staff=False)
        elif user_type == 'coach':
            qs = qs.filter(is_staff=True)
        return qs

    @staticmethod
    def get_serializer_for_user(user, action):
        if action == 'list':
            return UserSerializer
        if action == 'retrieve':
            if user.is_staff:
                return UserForCoachSerializer
            else:
                return UserForAthleteSerializer
        return UserSerializer