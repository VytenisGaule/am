from abc import ABC
from django.utils import timezone

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import generic
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from .models import *
from .forms import *


def index(request):
    if request.user.is_authenticated and request.user.groups.filter(name='players').exists():
        player_obj = Player.objects.get(player_user=request.user)
        num_visits = player_obj.num_visits
        last_visit = player_obj.last_visit
        player_obj.num_visits += 1
        player_obj.last_visit = timezone.now()
        player_obj.save()
    else:
        num_visits = request.session.get('num_visits', 1)
        last_visit = request.session.get('last_visit')
        request.session['num_visits'] = num_visits + 1
        request.session['last_visit'] = timezone.now().isoformat()
    data = {'num_visits_context': num_visits, 'last_visit_context': last_visit}
    return render(request, 'index.html', context=data)


@csrf_protect
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username %s already exists!!!" % username)
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email %s already exists!!!" % email)
        elif password != password2:
            messages.error(request, "Passwords doesn't match!!!")
        else:

            """strong password for later stages"""
            # try:
            #     password_validation.validate_password(password, request.user)
            # except ValidationError as er:
            #     for error in er:
            #         messages.error(request, error)
            #     return redirect('register_endpoint')

            User.objects.create_user(username=username, password=password, email=email)
            messages.info(request, "User %s registered successfully" % username)
            return redirect('login')
    return render(request, 'registration/register.html')


@login_required
def profilis(request):
    user = request.user
    if user.groups.filter(name='players').exists():
        profile = user.player
        form_class = PlayerUpdateForm
    else:
        raise Http404
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=user)
        profile_form = form_class(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and profile_form.is_valid():
            u_form.save()
            profile_form.save()
            messages.success(request, f"Profilis atnaujintas")
            return redirect('profile_endpoint')
    else:
        u_form = UserUpdateForm(instance=user)
        profile_form = form_class(instance=profile)
    data = {
        'u_form_cntx': u_form,
        'profile_form_cntx': profile_form,
    }
    return render(request, "profilis.html", context=data)


def search(request):
    """Todo list"""
    query_text = request.GET.get('search_text')
    return None


class PlayerSessionCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = PlayerSession
    template_name = 'player_new_session.html'
    form_class = PlayerSessionCreateForm

    def test_func(self):
        user = self.request.user
        player_id = self.kwargs.get('player_id')
        player = get_object_or_404(Player, id=player_id)
        return player.player_user == user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        player_id = self.kwargs.get('player_id')
        """todo list - pakeisti į aktyvią sesiją"""
        return reverse('index')
