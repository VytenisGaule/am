from .models import Player, PlayerSession, GameServer, TrackTarget, PlayerGameServer, Condition
from django_celery_beat.models import PeriodicTask
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import requests
from bs4 import BeautifulSoup
import json


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Nickname',
        }


class PlayerUpdateForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['nickname', 'avatar', 'timezone', 'active_time_start', 'active_time_end']


class PlayerSessionCreateForm(forms.ModelForm):
    login_url = forms.CharField(required=False)
    username = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['player'].initial = user.player

    def save(self, commit=True):
        session = super().save(commit=False)
        login_url = self.cleaned_data['login_url']
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        session_data = self.login(login_url, username, password)
        serialized_cookies = requests.utils.dict_from_cookiejar(
            session_data.cookies)  # Serialize cookies as a dictionary
        session.session_data = json.dumps(serialized_cookies)  # Serialize the cookies using JSON
        if commit:
            PlayerSession.objects.filter(player=session.player).update(is_active=False)
            session.save()
        return session

    @staticmethod
    def login(login_url, username, password):
        data = {'username': username, 'password': password, 'login': 'Login'}
        with requests.Session() as session:
            session.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/88.0.4324.190 Safari/537.36'
            }
            response = session.post(login_url, data=data)
            response.raise_for_status()
            return session

    class Meta:
        model = PlayerSession
        fields = ['login_url', 'username', 'password', 'player']
        widgets = {'player': forms.HiddenInput()}


class PlayerGameServerSelectForm(forms.ModelForm):
    game_server = forms.ModelMultipleChoiceField(
        queryset=GameServer.objects.all(),
        label='Select Game Server',
        required=False
    )

    class Meta:
        model = Player
        fields = ['game_server']


class PlayerTrackTargetCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        playergameserver_obj = kwargs.pop('playergameserver_obj')
        super().__init__(*args, **kwargs)
        self.fields['player_game_server'].widget = forms.HiddenInput()
        self.fields['player_game_server'].initial = playergameserver_obj
        self.fields['link'].widget.attrs[
            'value'] = f"https://{playergameserver_obj.game_server.name}.the-reincarnation.com/cgi-bin/"

    class Meta:
        model = TrackTarget
        fields = ['player_game_server', 'keyword', 'link', 'iterator_value']


class PlayerGameServerCreateForm(forms.ModelForm):
    class Meta:
        model = PlayerGameServer
        fields = ['period']
        widgets = {
            'period': forms.NumberInput(attrs={'min': 0}),
        }


class BaseModelForm(forms.ModelForm):
    class Meta:
        model = PeriodicTask
        fields = []


class ConditionCreateForm(forms.ModelForm):
    class Meta:
        model = Condition
        fields = ['operator']
        widgets = {
            'operator': forms.Select(),
        }
