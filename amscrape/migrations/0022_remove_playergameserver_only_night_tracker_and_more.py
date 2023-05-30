# Generated by Django 4.2.1 on 2023-05-29 22:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amscrape', '0021_playergameserver_only_night_tracker_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playergameserver',
            name='only_night_tracker',
        ),
        migrations.AlterField(
            model_name='player',
            name='last_visit',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 5, 30, 1, 6, 12, 540113), null=True, verbose_name='Last visit'),
        ),
        migrations.AlterField(
            model_name='playergameserver',
            name='period',
            field=models.PositiveIntegerField(default=1700, help_text='Average time to wait between tracking updates'),
        ),
    ]
