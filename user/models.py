from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random


def uid():
    return random.randint(9999999, 10000000000)


class User(AbstractUser):
    username = models.CharField(max_length=256, unique=True)
    id = models.BigIntegerField(primary_key=True, default=uid)
    email = models.EmailField(null=True, unique=True)
    created = models.DateTimeField(default=timezone.now)
    about = models.TextField(blank=True)
    verified = models.BooleanField(null=True, default=False)

    class Meta:
        ordering = ('-created', 'username')

    def __str__(self):
        return f"{self.username}"
