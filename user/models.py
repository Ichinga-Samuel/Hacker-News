from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    username = models.CharField(max_length=256, unique=True)
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(null=True, unique=True)
    created = models.DateTimeField(default=timezone.now)
    about = models.TextField(blank=True)
    verified = models.BooleanField(null=True, default=False)

    class Meta:
        ordering = ('-created', 'username')

    def __str__(self):
        return f"{self.username}"
