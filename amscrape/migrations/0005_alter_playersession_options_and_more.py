# Generated by Django 4.2.1 on 2023-05-19 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amscrape', '0004_rename_player_id_playersession_player'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='playersession',
            options={'ordering': ['is_active']},
        ),
        migrations.RemoveField(
            model_name='playersession',
            name='expire_date',
        ),
        migrations.AlterField(
            model_name='playersession',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
