from celery import shared_task
from .utils import get_scraped_data
from .models import PlayerGameServer, PlayerSession, TrackTarget, KingdomStat


@shared_task
def scrape_url_data_arch(player_game_server_id, active_session_id, track_target_ids):
    player_game_server = PlayerGameServer.objects.get(id=player_game_server_id)
    active_session = PlayerSession.objects.get(id=active_session_id)
    track_targets = TrackTarget.objects.filter(id__in=track_target_ids)
    values = get_scraped_data(track_targets, active_session.session_data)
    kingdom_stat = KingdomStat.objects.create(player_game_server=player_game_server, values=values)
    pass


@shared_task
def scrape_url_data_beta(player_game_server_id, active_session_id, track_target_ids):
    player_game_server = PlayerGameServer.objects.get(id=player_game_server_id)
    active_session = PlayerSession.objects.get(id=active_session_id)
    track_targets = TrackTarget.objects.filter(id__in=track_target_ids)
    values = get_scraped_data(track_targets, active_session.session_data)
    kingdom_stat = KingdomStat.objects.create(player_game_server=player_game_server, values=values)
    pass


@shared_task
def scrape_url_data_blitz(player_game_server_id, active_session_id, track_target_ids):
    player_game_server = PlayerGameServer.objects.get(id=player_game_server_id)
    active_session = PlayerSession.objects.get(id=active_session_id)
    track_targets = TrackTarget.objects.filter(id__in=track_target_ids)
    values = get_scraped_data(track_targets, active_session.session_data)
    kingdom_stat = KingdomStat.objects.create(player_game_server=player_game_server, values=values)
    pass


@shared_task
def scrape_url_data_guildwar(player_game_server_id, active_session_id, track_target_ids):
    player_game_server = PlayerGameServer.objects.get(id=player_game_server_id)
    active_session = PlayerSession.objects.get(id=active_session_id)
    track_targets = TrackTarget.objects.filter(id__in=track_target_ids)
    values = get_scraped_data(track_targets, active_session.session_data)
    kingdom_stat = KingdomStat.objects.create(player_game_server=player_game_server, values=values)
    pass


@shared_task
def scrape_url_data_lightning(player_game_server_id, active_session_id, track_target_ids):
    player_game_server = PlayerGameServer.objects.get(id=player_game_server_id)
    active_session = PlayerSession.objects.get(id=active_session_id)
    track_targets = TrackTarget.objects.filter(id__in=track_target_ids)
    values = get_scraped_data(track_targets, active_session.session_data)
    kingdom_stat = KingdomStat.objects.create(player_game_server=player_game_server, values=values)
    pass


@shared_task
def scrape_url_data_solo(player_game_server_id, active_session_id, track_target_ids):
    player_game_server = PlayerGameServer.objects.get(id=player_game_server_id)
    active_session = PlayerSession.objects.get(id=active_session_id)
    track_targets = TrackTarget.objects.filter(id__in=track_target_ids)
    values = get_scraped_data(track_targets, active_session.session_data)
    kingdom_stat = KingdomStat.objects.create(player_game_server=player_game_server, values=values)
    pass
