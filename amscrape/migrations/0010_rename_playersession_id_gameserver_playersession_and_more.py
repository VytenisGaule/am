# Generated by Django 4.2.1 on 2023-05-21 12:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amscrape', '0009_player_last_visit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gameserver',
            old_name='playersession_id',
            new_name='playersession',
        ),
        migrations.AlterField(
            model_name='player',
            name='last_visit',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 5, 21, 15, 59, 26, 41165), null=True, verbose_name='Last visit'),
        ),
    ]
