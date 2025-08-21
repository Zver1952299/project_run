from collections import defaultdict

from app_run.models import Challenge


class ChallengeSummaryService:
    @staticmethod
    def get_grouped_challenges():
        challenges = Challenge.objects.select_related('athlete').all()
        grouped = defaultdict(list)
        for i in challenges:
            athlete_data = {
                'id': i.athlete_id,
                'full_name': f"{i.athlete.first_name} {i.athlete.last_name}",
                'username': i.athlete.username
            }
            grouped[i.athlete.full_name].append(athlete_data)

        return [
            {'name_to_display': name, 'athletes': athletes}
            for name, athletes in grouped.items()
        ]