from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse


class Job(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(blank=True, default="No Title", max_length=256)
    time = models.DateTimeField(default=timezone.now)
    url = models.URLField(blank=True)
    text = models.TextField(blank=True)
    by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ('-time', 'title')

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse('jobs:job', args=(self.pk,))


class JobComments(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.TextField(blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    comment = models.ForeignKey('JobComments', on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time = models.DateTimeField(blank=True, default=timezone.now)

    def __str__(self):
        return f"{self.by}"
