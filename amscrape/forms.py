from .models import Player
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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
