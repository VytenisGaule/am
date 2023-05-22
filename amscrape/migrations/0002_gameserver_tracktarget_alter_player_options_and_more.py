# Generated by Django 4.2.1 on 2023-05-22 20:49

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('amscrape', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('arch', 'https://arch.the-reincarnation.com/cgi-bin/mainmenu.cgi'), ('guildwar', 'https://guildwar.the-reincarnation.com/cgi-bin/mainmenu.cgi'), ('blitz', 'https://blitz.the-reincarnation.com/cgi-bin/mainmenu.cgi'), ('solo', 'https://solo.the-reincarnation.com/cgi-bin/mainmenu.cgi'), ('lightning', 'https://lightning.the-reincarnation.com/cgi-bin/mainmenu.cgi'), ('beta', 'https://beta.the-reincarnation.com/cgi-bin/mainmenu.cgi')], default='beta', max_length=10, verbose_name='Server name')),
                ('oversummoning', models.BooleanField(default=True, help_text='True for oversummoning enviroment')),
                ('blackmarket', models.BooleanField(default=True, help_text='True if black market exists')),
                ('bots', models.BooleanField(default=True, help_text='True if AI exists')),
                ('ultimate', models.BooleanField(default=True, help_text='True if ultimate spells, units exists')),
                ('permanentuniques', models.BooleanField(default=True, help_text='True if uniques does not disappear')),
                ('period', models.PositiveIntegerField(default=0, help_text='Hours, usually "Damage" status last')),
                ('maxturns', models.PositiveIntegerField(default=0, help_text='Max turns available to reach')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TrackTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(default='', help_text='Keyword of tracking object, case sensitive', max_length=100)),
                ('link', models.CharField(default='', help_text='url - link where to search for object', max_length=200)),
                ('iterator_value', models.PositiveIntegerField(default=0, help_text='Index of value, if it is a table, first=0')),
            ],
        ),
        migrations.AlterModelOptions(
            name='player',
            options={'ordering': ['nickname'], 'permissions': [('can_edit_gameserver', 'Can edit owned gameserver parameters')]},
        ),
        migrations.AddField(
            model_name='player',
            name='last_visit',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 5, 22, 23, 49, 55, 915654), null=True, verbose_name='Last visit'),
        ),
        migrations.AddField(
            model_name='player',
            name='num_visits',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Visits'),
        ),
        migrations.CreateModel(
            name='PlayerSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_data', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amscrape.player')),
            ],
            options={
                'ordering': ['is_active'],
            },
        ),
        migrations.CreateModel(
            name='PlayerGameServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amscrape.gameserver')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amscrape.player')),
            ],
        ),
        migrations.CreateModel(
            name='KingdomStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('value', models.DecimalField(decimal_places=0, max_digits=12)),
                ('game_server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amscrape.gameserver')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amscrape.player')),
                ('track_target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amscrape.tracktarget')),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='game_server',
            field=models.ManyToManyField(blank=True, through='amscrape.PlayerGameServer', to='amscrape.gameserver'),
        ),
    ]
