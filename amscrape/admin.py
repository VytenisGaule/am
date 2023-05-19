from django.contrib import admin
from .models import Player


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'timezone', 'active_time_start', 'active_time_end')
    search_fields = ('nickname', 'timezone')


admin.site.register(Player, PlayerAdmin)