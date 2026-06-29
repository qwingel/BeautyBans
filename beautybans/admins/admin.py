from django.contrib import admin
from .models import Admin, AdminGroup, AdminServer


@admin.register(AdminGroup)
class AdminGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'flags', 'immunity', 'created_at')
    search_fields = ('name',)


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('name', 'steam_id', 'group', 'is_active', 'created_at')
    list_filter = ('is_active', 'group')
    search_fields = ('name', 'steam_id')


@admin.register(AdminServer)
class AdminServerAdmin(admin.ModelAdmin):
    list_display = ('admin', 'server', 'flags', 'immunity', 'created_at')
    list_filter = ('server',)
    search_fields = ('admin__name', 'server__name')
