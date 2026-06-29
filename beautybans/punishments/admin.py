from django.contrib import admin
from .models import Punishment


@admin.register(Punishment)
class PunishmentAdmin(admin.ModelAdmin):
    list_display = ('punishment_type', 'target_name', 'target_steam_id', 'target_ip', 'ban_subnet', 'admin', 'server', 'duration', 'is_active', 'issued_at')
    list_filter = ('punishment_type', 'is_active', 'ban_subnet', 'server')
    search_fields = ('target_name', 'target_steam_id', 'target_ip', 'reason')
    readonly_fields = ('issued_at', 'expires_at')
