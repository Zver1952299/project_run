from django.db import models
from django.contrib.auth.models import User


class Run(models.Model):
    class Status(models.TextChoices):
        INIT = 'init', 'Initialized'
        IN_PROGRESS = 'in_progress', 'In progress'
        FINISHED = 'finished', 'Finished'

    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INIT
    )