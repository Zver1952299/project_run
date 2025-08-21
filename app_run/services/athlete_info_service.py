from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from django.contrib.auth.models import User
from app_run.models import AthleteInfo
from app_run.serializers import AthleteInfoSerializer


class AthleteInfoService:
    @staticmethod
    def get_user_or_404(id):
        return get_object_or_404(User, id=id)

    @staticmethod
    def validate_weight(weight):
        if weight is None:
            return True
        try:
            weight = int(weight)
        except (TypeError, ValueError):
            return False
        return 0 < weight < 900

    @classmethod
    def get_or_create_athlete_info(cls, user_id):
        cls.get_user_or_404(user_id)

        obj, created = AthleteInfo.objects.get_or_create(
            user_id=user_id,
            defaults={'goals': '', 'weight': None}
        )
        return obj, created

    @staticmethod
    def build_response(obj, created, is_update=False):
        serializer = AthleteInfoSerializer(obj)
        status_code = status.HTTP_201_CREATED if created and is_update else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

    @classmethod
    def update_athlete_info(cls, user_id, goals=None, weight=None):
        cls.get_user_or_404(user_id)

        if not cls.validate_weight(weight):
            raise ValueError("Weight must be > 0 and < 900")

        obj, created = AthleteInfo.objects.update_or_create(
            user_id=user_id,
            defaults={
                'goals': goals or '',
                'weight': weight
            }
        )
        return obj, created