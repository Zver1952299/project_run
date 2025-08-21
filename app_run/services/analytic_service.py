from app_run.models import Subscribe, Run
from django.db.models import Sum, Avg


class AnalyticsService:
    @staticmethod
    def get_coach_analytics(coach_id: int):
        athlete_ids = Subscribe.objects.filter(coach_id=coach_id).values_list('athlete_id', flat=True)

        longest_run = (
            Run.objects
            .filter(athlete_id__in=athlete_ids, status=Run.Status.FINISHED)
            .order_by('-distance')
            .values('athlete_id', 'distance')
            .first()
        )

        total_run = (
            Run.objects
            .filter(athlete_id__in=athlete_ids, status=Run.Status.FINISHED)
            .values('athlete_id')
            .annotate(total_distance=Sum('distance'))
            .order_by('-total_distance')
            .first()
        )

        speed_avg = (
            Run.objects
            .filter(athlete_id__in=athlete_ids, status=Run.Status.FINISHED)
            .values('athlete_id')
            .annotate(avg_speed_m_s=Avg('speed'))
            .order_by('-avg_speed_m_s')
            .first()
        )

        return {
            "longest_run_user": longest_run["athlete_id"] if longest_run else None,
            "longest_run_value": longest_run["distance"] if longest_run else None,

            "total_run_user": total_run["athlete_id"] if total_run else None,
            "total_run_value": total_run["total_distance"] if total_run else None,

            "speed_avg_user": speed_avg["athlete_id"] if speed_avg else None,
            "speed_avg_value": speed_avg["avg_speed_m_s"] if speed_avg else None,
        }