from django.db import models

from account.models import User, Base


class Story(Base):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name='stories', on_delete=models.CASCADE)
    url = models.URLField(blank=True)
    text = models.TextField(blank=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.title}'

    class Meta(Base.Meta):
        db_table = 'story'
        abstract = False


class Comment(Base):
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    story = models.ForeignKey(Story, related_name='comments', on_delete=models.CASCADE, null=True, default=None)
    reply = models.ManyToManyField('Comment', related_name='replies')

    def __str__(self):
        return f'{self.text[:15]}'

    class Meta(Base.Meta):
        db_table = 'comment'
        abstract = False
