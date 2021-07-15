from django.db import models
from django.utils import timezone
from django.conf import settings


class Poll(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(blank=True, default="No Title", max_length=256)
    time = models.DateTimeField(blank=True, default=timezone.now)
    text = models.TextField(blank=True, null=True)
    by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reviews = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.title}'


class PollOptions(models.Model):
    id = models.IntegerField(primary_key=True)
    votes = models.IntegerField(default=0, blank=True)
    text = models.TextField(blank=True, default=' ')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')

    def __str__(self):
        return f'{self.text}'


class PollComments(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.TextField(blank=True, null=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    comment = models.ForeignKey('PollComments', on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time = models.DateTimeField(blank=True, default=timezone.now)

    def __str__(self):
        return f"{self.by}"
