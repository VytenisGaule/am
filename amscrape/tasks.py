from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from .utils import get_scraped_data
from .models import PlayerGameServer, PlayerSession, TrackTarget, KingdomStat, Rule
import json


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
    rules_queryset = Rule.objects.filter(conditions__track_target__in=track_targets).distinct()
    for rule in rules_queryset:
        conditions = rule.conditions.all()
        all_conditions_satisfied = True
        for condition in conditions:
            track_target = condition.track_target
            if str(track_target) in values:
                parsed_values = json.loads(values)
                condition_values = parsed_values.get(str(track_target))
                for value in condition_values:
                    try:
                        desired_value = int(value)
                    except ValueError:
                        desired_value = value
                    if condition.compare_values(desired_value):
                        continue
                    else:
                        print('One of conditions is False')
                        all_conditions_satisfied = False
                        break
            else:
                all_conditions_satisfied = False
                print('condition is not tracked, False')
                break
        if all_conditions_satisfied:
            print('conditions True')
            print(rule.passive_function)
            rule.perform_reaction()
    pass
