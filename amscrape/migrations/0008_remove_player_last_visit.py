# Generated by Django 4.2.1 on 2023-05-19 22:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('amscrape', '0007_player_last_visit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='last_visit',
        ),
    ]
