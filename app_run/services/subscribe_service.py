from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from app_run.services.run_service import get_user_or_400
from app_run.models import Subscribe


class SubscribeService:
    @staticmethod
    def subscribe(athlete_id, coach_id):
        athlete = get_user_or_400(athlete_id)
        coach = get_object_or_404(User, id=coach_id)
        if athlete.is_staff or not coach.is_staff:
            raise ValueError("Only athletes can subscribe to coaches")
        subscription, created = Subscribe.objects.get_or_create(athlete=athlete, coach=coach)
        if not created:
            raise ValueError("Already subscribed")
        return subscription

    @staticmethod
    def rate(athlete_id, coach_id, rating):
        subscribe = Subscribe.objects.filter(coach_id=coach_id, athlete_id=athlete_id).first()
        if not subscribe:
            raise ValueError("Subscription not found")
        if rating is None or not str(rating).isdigit():
            raise ValueError("Invalid rating")
        subscribe.rating = rating
        subscribe.save()
        return subscribe