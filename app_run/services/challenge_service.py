from app_run.models import Challenge
from app_run.serializers import ChallengeSerializer


class ChallengeService:
    @staticmethod
    def get_challenges(athlete=None):
        qs = Challenge.objects.all()
        if athlete:
            qs = qs.filter(athlete=athlete)
        return qs

    @staticmethod
    def serialize_challenges(qs):
        return ChallengeSerializer(qs, many=True).data