from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.conf import settings
from .models import Player


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name='players')
        instance.groups.add(group)


@receiver(m2m_changed, sender=User.groups.through)
def update_player(sender, instance, action, model, **kwargs):
    if action == 'post_add' and model == Group and 'players' in Group.objects.filter(
            pk__in=kwargs['pk_set']).values_list('name', flat=True):
        Player.objects.get_or_create(player_user=instance)
    elif action == 'post_remove' and model == Group and not instance.groups.filter(name='players').exists():
        try:
            player = instance.player
            player.delete()
        except Player.DoesNotExist:
            pass

