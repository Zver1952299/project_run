from app_run.models import Position, CollectibleItem
from haversine import haversine, Unit


class PositionService:
    @staticmethod
    def update_collectibles_and_stats(position):
        athlete = position.run.athlete
        items = CollectibleItem.objects.all()
        for i in items:
            distance = haversine((position.latitude, position.longitude), (i.latitude, i.longitude), unit=Unit.METERS)
            if distance < 100:
                athlete.collectible_items.add(i)

        positions_of_run = Position.objects.filter(run=position.run).order_by('date_time')
        if positions_of_run.count() > 1:
            last_position = positions_of_run.last()
            prev_position = positions_of_run[positions_of_run.count() - 2]
            distance_between = haversine((prev_position.latitude, prev_position.longitude),
                                         (last_position.latitude, last_position.longitude), unit=Unit.METERS)
            last_position.distance = round(prev_position.distance + distance_between, 2)
            time_diff = (last_position.date_time - prev_position.date_time).total_seconds()
            last_position.speed = round(distance_between / time_diff, 2)
            last_position.save()