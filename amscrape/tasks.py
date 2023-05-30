from django_celery_beat.models import PeriodicTask, IntervalSchedule
from celery import shared_task
from .utils import get_scraped_data
from .models import PlayerGameServer, PlayerSession, TrackTarget, KingdomStat
import time
import json


@shared_task
def scrape_url_data(player_game_server_id, active_session_id, track_target_ids):
    player_game_server = PlayerGameServer.objects.get(id=player_game_server_id)
    active_session = PlayerSession.objects.get(id=active_session_id)
    track_targets = TrackTarget.objects.filter(id__in=track_target_ids)
    values = get_scraped_data(track_targets, active_session.session_data)
    kingdom_stat = KingdomStat.objects.create(player_game_server=player_game_server, values=values)
    pass


def schedule_scrape_task(schedule_minutes, player_game_server_id, session_id, track_target_ids):
    interval, _ = IntervalSchedule.objects.get_or_create(every=schedule_minutes, period=IntervalSchedule.MINUTES)
    task, _ = PeriodicTask.objects.update_or_create(
        name='scrape_url_data',
        defaults={
            'task': 'amscrape.tasks.scrape_url_data',
            'interval': interval,
            'enabled': True,
        }
    )
    task.args = json.dumps([player_game_server_id, session_id, track_target_ids])
    task.save()
