from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


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
    run_time_seconds = models.PositiveIntegerField(default=0)
    speed = models.FloatField(default=0.0)

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
    date_time = models.DateTimeField(default=timezone.now)
    speed = models.FloatField(default=0.0)
    distance = models.FloatField(default=0.0)


class CollectibleItem(models.Model):
    name = models.CharField(max_length=200)
    uid = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=6, decimal_places=4)
    longitude = models.DecimalField(max_digits=7, decimal_places=4)
    picture = models.URLField()
    value = models.IntegerField()
    athletes = models.ManyToManyField(User, related_name='collectible_items')


class Subscribe(models.Model):
    athlete = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        unique_together = ['athlete', 'coach']