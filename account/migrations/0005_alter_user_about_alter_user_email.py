# Generated by Django 4.2.5 on 2023-10-04 00:36

import account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='about',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(default=account.models.get_email, max_length=255, primary_key=True, serialize=False, unique=True),
        ),
    ]
