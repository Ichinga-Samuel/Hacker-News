from django.db import models

from account.models import User, Base


class Poll(Base):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name='polls', on_delete=models.CASCADE)
    text = models.TextField(blank=True, default='')
    score = models.IntegerField(default=0)

    class Meta(Base.Meta):
        db_table = 'poll'
        abstract = False


class PollOption(Base):
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    class Meta(Base.Meta):
        db_table = 'poll_option'
        abstract = False
