from django.contrib import admin
from .models import Player, GameServer


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'timezone', 'active_time_start', 'active_time_end')
    search_fields = ('nickname', 'timezone')


class GameServerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'period', 'maxturns')


admin.site.register(Player, PlayerAdmin)
admin.site.register(GameServer, GameServerAdmin)
