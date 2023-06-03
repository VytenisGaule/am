from django.utils import timezone
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
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .forms import *
from .tasks import scrape_url_data
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json


class PlayerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        player = get_object_or_404(Player, player_user=user)
        return player is not None


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
            # except ValidationError as e:
            #     for error in e:
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


class PlayerSessionCreateView(LoginRequiredMixin, PlayerRequiredMixin, generic.CreateView):
    model = PlayerSession
    template_name = 'player_new_session.html'
    form_class = PlayerSessionCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        player_id = self.kwargs.get('player_id')
        return reverse('index')


class GameServerListView(LoginRequiredMixin, PlayerRequiredMixin, generic.ListView):
    model = PlayerGameServer
    template_name = 'player_server_list.html'

    def get_queryset(self):
        user = self.request.user
        player = get_object_or_404(Player, player_user=user)
        return PlayerGameServer.objects.filter(player=player)


class PlayerGameServerSelectView(LoginRequiredMixin, PlayerRequiredMixin, generic.FormView):
    template_name = 'player_select_server.html'
    form_class = PlayerGameServerSelectForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = get_object_or_404(Player, player_user=self.request.user)
        playergameserver_list = PlayerGameServer.objects.filter(player=player)
        context['gameserver_list'] = GameServer.objects.all()
        context['playergameserver_ids'] = set(playergameserver_list.values_list('game_server_id', flat=True))
        context['playergameserver'] = set(player.playergameserver_set.all())
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.user = self.request.user
        return form

    def form_valid(self, form):
        player = get_object_or_404(Player, player_user=self.request.user)
        selected_servers = form.cleaned_data['game_server'].all()
        removed_servers = GameServer.objects.exclude(id__in=selected_servers.values_list('id', flat=True))
        for server in removed_servers:
            try:
                player_game_server = PlayerGameServer.objects.get(player=player, game_server=server)
                if player_game_server.periodic_task:
                    player_game_server.periodic_task.delete()
                    player_game_server.delete()
            except ObjectDoesNotExist:
                pass
        player.game_server.set(selected_servers)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('servers_endpoint', kwargs={'player_id': self.request.user.player.id})


class ServerDetailView(LoginRequiredMixin, PlayerRequiredMixin, generic.DetailView):
    model = PlayerGameServer
    template_name = 'server_detail.html'
    context_object_name = 'player_game_server'


class PlayerTrackTargetListView(LoginRequiredMixin, PlayerRequiredMixin, generic.ListView):
    model = TrackTarget
    template_name = 'player_track_target_list.html'
    context_object_name = 'track_targets'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player_game_server = PlayerGameServer.objects.get(pk=self.kwargs['player_game_server_id'])
        context['player_game_server'] = player_game_server
        return context

    def get_queryset(self):
        player_game_server_id = self.kwargs['player_game_server_id']
        return TrackTarget.objects.filter(player_game_server_id=player_game_server_id)

    def post(self, request, *args, **kwargs):
        player_game_server_id = self.kwargs['player_game_server_id']
        delete_pk = request.POST.get('delete_pk')

        if delete_pk:
            tracking_obj = get_object_or_404(TrackTarget, pk=delete_pk)
            tracking_obj.delete()

        return redirect('server_trackers_endpoint', player_game_server_id=player_game_server_id)


class PlayerTrackTargetCreateView(LoginRequiredMixin, PlayerRequiredMixin, generic.CreateView):
    model = TrackTarget
    template_name = 'new_tracking_object.html'
    form_class = PlayerTrackTargetCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        player_game_server_id = self.kwargs['player_game_server_id']
        playergameserver_obj = get_object_or_404(PlayerGameServer, id=player_game_server_id)
        kwargs['playergameserver_obj'] = playergameserver_obj
        return kwargs

    def get_success_url(self):
        return reverse_lazy('server_trackers_endpoint',
                            kwargs={'player_game_server_id': self.object.player_game_server_id})


class PlayerGameServerUpdateView(LoginRequiredMixin, PlayerRequiredMixin, generic.UpdateView):
    model = PlayerGameServer
    template_name = 'game_server_parameters.html'
    form_class = PlayerGameServerCreateForm

    def get_success_url(self):
        return reverse_lazy('server_endpoint', kwargs={
            'pk': self.kwargs['pk']})


class PeriodicTaskCreateView(LoginRequiredMixin, PlayerRequiredMixin, generic.CreateView):
    model = PeriodicTask
    template_name = 'create_periodic_task.html'
    form_class = BaseModelForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        player_game_server = get_object_or_404(PlayerGameServer, id=self.kwargs['player_game_server_id'])
        interval, _ = IntervalSchedule.objects.get_or_create(
            every=player_game_server.period,
            period=IntervalSchedule.MINUTES
        )
        form.instance.interval = interval
        return form

    def form_valid(self, form):
        player_game_server = get_object_or_404(PlayerGameServer, id=self.kwargs['player_game_server_id'])
        active_session = get_object_or_404(PlayerSession, player=player_game_server.player, is_active=True)
        track_target_ids = list(
            TrackTarget.objects.filter(player_game_server=player_game_server).values_list('id', flat=True)
        )
        session_id = active_session.id
        existing_task = PeriodicTask.objects.filter(playergameserver=player_game_server).first()
        interval = form.instance.interval
        if existing_task:
            existing_task.interval = interval
            existing_task.enabled = True
            existing_task.args = json.dumps([player_game_server.id, active_session.id, track_target_ids])
            existing_task.save()
        else:
            task = PeriodicTask.objects.create(
                name=f'{player_game_server.id}',
                task='amscrape.tasks.scrape_url_data',
                interval=interval,
                enabled=True,
            )
            task.args = json.dumps([player_game_server.id, session_id, track_target_ids])
            task.save()
            player_game_server.periodic_task = task
            player_game_server.save()
            scrape_url_data.apply_async(args=[player_game_server.id, session_id, track_target_ids],
                                        task_id=f'scrape_url_data_{player_game_server.id}')
        return redirect(
            reverse('server_trackers_endpoint', kwargs={'player_game_server_id': player_game_server.id}))


class PeriodicTaskPauseView(LoginRequiredMixin, PlayerRequiredMixin, generic.FormView):
    model = PeriodicTask
    template_name = 'stop_periodic_task.html'
    form_class = BaseModelForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        player_game_server = get_object_or_404(PlayerGameServer, id=self.kwargs['player_game_server_id'])
        interval, _ = IntervalSchedule.objects.get_or_create(
            every=player_game_server.period,
            period=IntervalSchedule.MINUTES
        )
        form.instance.interval = interval
        return form

    def form_valid(self, form):
        player_game_server = get_object_or_404(PlayerGameServer, id=self.kwargs['player_game_server_id'])
        existing_task = PeriodicTask.objects.filter(playergameserver=player_game_server).first()
        existing_task.enabled = False
        existing_task.save()
        return redirect(reverse('server_trackers_endpoint', kwargs={'player_game_server_id': player_game_server.id}))


class KingdomStatListView(LoginRequiredMixin, PlayerRequiredMixin, generic.ListView):
    model = KingdomStat
    template_name = 'kingdom_stat_list.html'

    def get_queryset(self):
        player_game_server_id = self.kwargs['player_game_server_id']
        queryset = KingdomStat.objects.filter(player_game_server_id=player_game_server_id)
        for obj in queryset:
            obj.values = json.loads(obj.values)
        json_data_list = [kingdomstat.values for kingdomstat in queryset]
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player_game_server = PlayerGameServer.objects.get(pk=self.kwargs['player_game_server_id'])
        kingdomstat_list = self.get_queryset()
        json_data_list = [kingdomstat.values for kingdomstat in kingdomstat_list]
        json_keys_set = set()
        for json_data in json_data_list:
            json_keys_set.update(json_data.keys())
        json_keys_list = sorted(json_keys_set)
        context['json_keys_list'] = json_keys_list
        context['player_game_server'] = player_game_server
        return context


class KingdomStatFilteredListView(LoginRequiredMixin, PlayerRequiredMixin, generic.ListView):
    model = KingdomStat
    template_name = 'kingdom_stat_filter_list.html'

    def get_queryset(self):
        player_game_server_id = self.kwargs['player_game_server_id']
        selected_key = self.kwargs['selected_key']
        queryset = KingdomStat.objects.filter(player_game_server_id=player_game_server_id)
        filtered_data = []
        for obj in queryset:
            obj.values = json.loads(obj.values)
            if selected_key in obj.values:
                filtered_data.append((obj.timestamp, obj.values[selected_key]))
        queryset = []
        for i in range(len(filtered_data)):
            if i == 0 or filtered_data[i][1] != filtered_data[i-1][1]:
                queryset.append(filtered_data[i])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player_game_server = PlayerGameServer.objects.get(pk=self.kwargs['player_game_server_id'])
        kingdomstat_list = self.get_queryset()
        selected_key = self.kwargs['selected_key']
        context['selected_key'] = selected_key
        context['player_game_server'] = player_game_server
        context['kingdomstat_list'] = kingdomstat_list
        return context
