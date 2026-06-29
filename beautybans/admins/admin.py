from django.contrib import admin
from .models import Admin, AdminGroup, AdminServer


@admin.register(AdminGroup)
class AdminGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'flags', 'immunity', 'created_at')
    search_fields = ('name',)


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('name', 'steam_id', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'steam_id')


@admin.register(AdminServer)
class AdminServerAdmin(admin.ModelAdmin):
    list_display = ('admin', 'server', 'group', 'flags', 'immunity', 'created_at')
    list_filter = ('server', 'group')
    search_fields = ('admin__name', 'server__name')
