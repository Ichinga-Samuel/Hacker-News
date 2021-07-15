from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse


class Story(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(default="No Title", max_length=256)
    time = models.DateTimeField(default=timezone.now)
    url = models.URLField(blank=True)
    score = models.IntegerField(default=0)
    text = models.TextField(blank=True)
    by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reviews = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'
        ordering = ('-time', '-score', '-reviews')

    def __str__(self):
        return f'{self.title}'

    def add_score(self, score):
        self.score += score

    def get_absolute_url(self):
        return reverse('news:story', kwargs={'pk': self.pk})


class StoryComments(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.TextField(blank=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    comment = models.ForeignKey('StoryComments', on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ('-time', )

    def __str__(self):
        return f"By {self.by}"



