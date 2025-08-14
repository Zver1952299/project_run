from django.db import models
from django.contrib.auth.models import User


class Run(models.Model):
    class Status(models.TextChoices):
        INIT = 'init', 'Initialized'
        IN_PROGRESS = 'in_progress', 'In progress'
        FINISHED = 'finished', 'Finished'

    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name='runs')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INIT
    )
    distance = models.FloatField(null=True, blank=True)

class AthleteInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='info')
    goals = models.TextField(blank=True)
    weight = models.IntegerField(null=True, blank=True)


class Challenge(models.Model):
    full_name = models.CharField(max_length=200)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=6, decimal_places=4)
    longitude = models.DecimalField(max_digits=7, decimal_places=4)