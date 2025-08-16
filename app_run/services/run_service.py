from app_run.models import Run, Challenge
from django.db.models import Q, Count, Sum, Min, Max, Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from haversine import haversine


class RunService:
    allowed_transitions = {
        'start': (Run.Status.INIT, Run.Status.IN_PROGRESS),
        'stop': (Run.Status.IN_PROGRESS, Run.Status.FINISHED)
    }

    @classmethod
    def update_status(cls, id, action):
        if action not in cls.allowed_transitions:
            raise ValueError("Invalid action")

        expected_status, new_status = cls.allowed_transitions[action]
        run = get_object_or_404(Run, id=id)

        if run.status != expected_status:
            raise RuntimeError(f"The run status isn't '{expected_status}'")

        run.status = new_status

        if action == 'stop':
            run.distance = cls._calculating_distance(run)
            run.run_time_seconds = cls._calculate_total_distance(run)
            run.speed = cls._calculate_average_speed(run)
            cls._check_challenges(run)

        run.save()

        return run

    @staticmethod
    def _check_challenges(run):
        user = (
            User.objects
            .annotate(
                runs_finished=Count(
                    'runs',
                    filter=Q(runs__status=Run.Status.FINISHED)
                )
            )
            .get(id=run.athlete_id)
        )

        if user.runs_finished == 10:
            Challenge.objects.create(full_name="Сделай 10 Забегов!", athlete=user)

        total_distance = Run.objects.filter(athlete=user).aggregate(sum=Sum('distance'))
        if total_distance['sum'] >= 50:
            Challenge.objects.create(full_name="Пробеги 50 километров!", athlete=user)

        if run.distance >= 2 and run.run_time_seconds <= 600:
            Challenge.objects.create(full_name="2 километра за 10 минут!", athlete=user)

    @staticmethod
    def _calculating_distance(run):
        qs = run.position_set.values()
        distance = 0
        if len(qs):
            for point in range(len(qs) - 1):
                distance += haversine((qs[point]['latitude'], qs[point]['longitude']), (qs[point + 1]['latitude'], qs[point + 1]['longitude']))

        return round(distance, ndigits=3)

    @staticmethod
    def _calculate_total_distance(run):
        qs = run.position_set.aggregate(
            pos_earliest=Min('date_time'),
            pos_latest=Max('date_time')
        )
        if not qs['pos_latest'] and not qs['pos_earliest']:
            return 0

        seconds = (qs['pos_latest'] - qs['pos_earliest']).total_seconds()

        return seconds

    @staticmethod
    def _calculate_average_speed(run):
        average_speed = run.position_set.aggregate(Avg('speed'))
        return round(average_speed['speed__avg'], ndigits=2)
