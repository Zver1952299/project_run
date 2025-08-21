from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from app_run.models import Subscribe
from app_run.serializers import SubscribeSerializer


class RatingService:
    @staticmethod
    def rate_athlete(coach_id: int, athlete_id: int, rating):
        athlete = User.objects.filter(id=athlete_id).first()
        if not athlete:
            return {'error': 'Invalid athlete_id', 'status': 400}

        coach = get_object_or_404(User, id=coach_id)
        if int(athlete_id) not in coach.subscribers.values_list("athlete_id", flat=True):
            return {'error': 'Athlete is not subscribed to coach', 'status': 400}

        subscribe = Subscribe.objects.filter(coach_id=coach_id, athlete_id=athlete_id).first()
        if not subscribe:
            return {'error': 'Subscription not found', 'status': 400}

        if rating is None or not str(rating).isdigit():
            return {'error': 'rating is invalid', 'status': 400}

        serializer = SubscribeSerializer(subscribe, data={'rating': rating}, partial=True)
        if serializer.is_valid():
            subscribe.rating = rating
            subscribe.save()
            return {'success': 'Rating has been saved'}
        else:
            return {'error': serializer.errors['rating'][0], 'status': 400}