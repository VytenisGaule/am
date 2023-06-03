from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from .utils import get_scraped_data
from .models import PlayerGameServer, PlayerSession, TrackTarget, KingdomStat


@shared_task
def scrape_url_data(player_game_server_id, active_session_id, track_target_ids):
    try:
        player_game_server = PlayerGameServer.objects.get(pk=player_game_server_id)
    except ObjectDoesNotExist:
        return
    active_session = PlayerSession.objects.get(id=active_session_id)
    track_targets = TrackTarget.objects.filter(id__in=track_target_ids)
    values = get_scraped_data(track_targets, active_session.session_data)
    try:
        kingdom_stat = KingdomStat.objects.create(player_game_server=player_game_server, values=values)
    except Exception as e:
        return
    pass
