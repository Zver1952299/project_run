from app_run.models import Run, Challenge
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


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
        run.save()

        if action == 'stop':
            cls._check_challenges(run)

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