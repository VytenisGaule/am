from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from PIL import Image
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, time


class GameServer(models.Model):
    """Server stats, user can edit own preferences whenever it changes"""
    SERVER_URL_ENDPOINTS = (
        ('arch', 'https://arch.the-reincarnation.com/cgi-bin/mainmenu.cgi'),
        ('guildwar', 'https://guildwar.the-reincarnation.com/cgi-bin/mainmenu.cgi'),
        ('blitz', 'https://blitz.the-reincarnation.com/cgi-bin/mainmenu.cgi'),
        ('solo', 'https://solo.the-reincarnation.com/cgi-bin/mainmenu.cgi'),
        ('lightning', 'https://lightning.the-reincarnation.com/cgi-bin/mainmenu.cgi'),
        ('beta', 'https://beta.the-reincarnation.com/cgi-bin/mainmenu.cgi'),
    )
    name = models.CharField('Server name', max_length=10, choices=SERVER_URL_ENDPOINTS, default='beta')
    oversummoning = models.BooleanField(default=True, help_text='True for oversummoning enviroment')
    blackmarket = models.BooleanField(default=True, help_text='True if black market exists')
    bots = models.BooleanField(default=True, help_text='True if AI exists')
    ultimate = models.BooleanField(default=True, help_text='True if ultimate spells, units exists')
    permanentuniques = models.BooleanField(default=True, help_text='True if uniques does not disappear')
    period = models.PositiveIntegerField(default=0, help_text='Hours, usually "Damage" status last')
    maxturns = models.PositiveIntegerField(default=0, help_text='Max turns available to reach')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['name']


class Player(models.Model):
    """Django user assigned to control player profile"""
    player_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player')
    game_server = models.ManyToManyField(GameServer, through='PlayerGameServer', blank=True)
    nickname = models.CharField('Nickname', max_length=100)
    avatar = models.ImageField(default='profile_pics/default.png', upload_to='profile_pics')
    TIME_ZONES = (
        ('UTC', 'Universal Coordinated Time GMT'),
        ('ECT', 'European Central Time GMT+1:00'),
        ('EET', 'Eastern European Time GMT+2:00'),
        ('ART', '(Arabic) Egypt Standard Time GMT+2:00'),
        ('EAT', 'Eastern African Time GMT+3:00'),
        ('MET', 'Middle East Time GMT+3:30'),
        ('NET', 'Near East Time GMT+4:00'),
        ('PLT', 'Pakistan Lahore Time GMT+5:00'),
        ('IST', 'India Standard Time GMT+5:30'),
        ('BST', 'Bangladesh Standard Time GMT+6:00'),
        ('VST', 'Vietnam Standard Time GMT+7:00'),
        ('CTT', 'China Taiwan Time GMT+8:00'),
        ('JST', 'Japan Standard Time GMT+9:00'),
        ('ACT', 'Australia Central Time GMT+9:30'),
        ('AET', 'Australia Eastern Time GMT+10:00'),
        ('SST', 'Solomon Standard Time GMT+11:00'),
        ('NST', 'New Zealand Standard Time GMT+12:00'),
        ('MIT', 'Midway Islands Time GMT-11:00'),
        ('HST', 'Hawaii Standard Time GMT-10:00'),
        ('AST', 'Alaska Standard Time GMT-9:00'),
        ('PST', 'Pacific Standard Time GMT-8:00'),
        ('PNT', 'Phoenix Standard Time GMT-7:00'),
        ('MST', 'Mountain Standard Time GMT-7:00'),
        ('CST', 'Central Standard Time GMT-6:00'),
        ('EST', 'Eastern Standard Time GMT-5:00'),
        ('IET', 'Indiana Eastern Standard Time GMT-5:00'),
        ('PRT', 'Puerto Rico and US Virgin Islands Time GMT-4:00'),
        ('CNT', 'Canada Newfoundland Time GMT-3:30'),
        ('AGT', 'Argentina Standard Time GMT-3:00'),
        ('BET', 'Brazil Eastern Time GMT-3:00'),
        ('CAT', 'Central African Time GMT-1:00')
    )
    timezone = models.CharField('timezone', max_length=3, choices=TIME_ZONES, default='EET')
    active_time_start = models.TimeField(default=time(hour=9, minute=0))
    active_time_end = models.TimeField(default=time(hour=23, minute=0))
    num_visits = models.IntegerField('Visits', default=0, null=True, blank=True)
    last_visit = models.DateTimeField('Last visit', default=datetime.now(), null=True, blank=True)

    class Meta:
        ordering = ['nickname']
        permissions = [
            ('can_edit_gameserver', 'Can edit owned gameserver parameters'),
        ]

    def __str__(self):
        return f'{self.nickname}'

    @property
    def absolute_time_difference(self):
        server_timezone = pytz.timezone('EET')
        server_time = datetime.now(server_timezone)
        user_timezone = pytz.timezone(self.timezone)
        user_time = server_time.astimezone(user_timezone)
        return abs(user_time - server_time)


class PlayerGameServer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game_server = models.ForeignKey(GameServer, on_delete=models.CASCADE)
    period = models.PositiveIntegerField(default=1700, help_text='Average time to wait between tracking updates')

    def __str__(self):
        return f"{self.game_server} - {self.period} seconds"


class PlayerSession(models.Model):
    """Django saving session data, but not player login credentials"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    session_data = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Session for Player: {self.player}'

    class Meta:
        ordering = ['is_active']

    @property
    def active_session(self):
        return self.playersession_set.order_by('-id').first()


class TrackTarget(models.Model):
    player_game_server = models.ForeignKey(PlayerGameServer, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=100, default='', help_text='Keyword of tracking object, case sensitive')
    link = models.CharField(max_length=200, default='', help_text='url - link where to search for object')
    iterator_value = models.PositiveIntegerField(default=0, help_text='Index of value, if it is a table, first=0')

    def __str__(self):
        return self.keyword


class KingdomStat(models.Model):
    player_game_server = models.ForeignKey(PlayerGameServer, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    values = models.JSONField()

    def __str__(self):
        return f'{self.timestamp}'
