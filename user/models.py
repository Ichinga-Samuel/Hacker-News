from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    username = models.CharField(max_length=256, unique=True)
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(null=True, unique=True)
    created = models.DateTimeField(default=timezone.now)
    about = models.TextField(blank=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f"{self.username}"
