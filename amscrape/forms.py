from .models import Player, PlayerSession, GameServer, TrackTarget, PlayerGameServer
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import requests
from bs4 import BeautifulSoup


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
        session.session_data = session_data
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
            cookies = session.cookies.get_dict()
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
        gameserver_obj = kwargs.pop('gameserver_obj')
        super().__init__(*args, **kwargs)
        self.fields['link'].widget.attrs['value'] = f"https://{gameserver_obj.name}.the-reincarnation.com/cgi-bin/"

    class Meta:
        model = TrackTarget
        fields = ['keyword', 'link', 'keyword', 'iterator_value']


class PlayerGameServerCreateForm(forms.ModelForm):
    def __init__(self, *args, gameserver_obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.gameserver_obj = gameserver_obj

    class Meta:
        model = PlayerGameServer
        fields = ['period']
