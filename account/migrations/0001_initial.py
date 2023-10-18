# Generated by Django 4.2.1 on 2023-08-19 21:07

import account.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(default=account.models.get_email, max_length=255, primary_key=True, serialize=False, unique=True)),
                ('username', models.CharField(max_length=255, unique=True)),
                ('karma', models.IntegerField(default=0)),
                ('verified', models.BooleanField(default=False)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('about', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'user',
                'abstract': False,
                'unique_together': {('email', 'username')},
            },
        ),
    ]