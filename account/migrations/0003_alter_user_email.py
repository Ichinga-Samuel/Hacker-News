# Generated by Django 4.2.1 on 2023-09-16 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=255, primary_key=True, serialize=False, unique=True),
        ),
    ]