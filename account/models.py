from random import shuffle

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.urls import reverse
from django.utils.timezone import now


def get_email():
    chars = [chr(i) for i in range(97, 123)]
    shuffle(chars)
    return f"{''.join(chars[:10])}@gmail.com"


class Type(models.TextChoices):
    JOB = 'job'
    STORY = 'story'
    COMMENT = 'comment'
    POLL = 'poll'
    POLLOPT = 'pollopt'


def get_id():
    ids = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    shuffle(ids)
    return int(''.join(ids[:]))


class Base(models.Model):
    id = models.BigIntegerField(primary_key=True, default=get_id)
    type = models.CharField(choices=Type.choices)
    created = models.DateTimeField(default=now)
    deleted = models.BooleanField(default=False)
    dead = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        if self.type in ('job', 'story', 'poll'):
            return reverse(f'{self.type}-detail', kwargs={'type': self.type, 'pk': self.pk})
        if self.type == 'comment':
            return self.story.get_absolute_url()
        if self.type == 'pollopt':
            return self.poll.get_absolute_url()

    def get_edit_url(self):
        return reverse('story-update', kwargs={'type': self.type, 'pk': self.pk})
    
    class Meta:
        abstract = True
        ordering = ['created']


class UserManager(BaseUserManager):
    def create_user(self, *, username: str, email: str = '', password: str = '', **kwargs):
        user = self.model(email=self.normalize_email(email), username=username, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, *, email: str, username: str, password: str = ''):
        self.create_user(email=email, username=username, password=password, verified=True, is_admin=True)
        
        
class User(AbstractBaseUser):
    email = models.EmailField(unique=True, primary_key=True, max_length=255, default=get_email)
    username = models.CharField(unique=True, max_length=255)
    karma = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    created = models.DateTimeField(default=now)
    about = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ('username', )
    
    objects = UserManager()

    def __str__(self):
        return str(self.username)
    
    class Meta(AbstractBaseUser.Meta):
        unique_together = ('email', 'username')
        db_table = 'user'
    
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin
    