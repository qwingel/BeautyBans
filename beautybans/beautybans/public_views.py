from django.shortcuts import render
from punishments.models import Punishment
from admins.models import Admin, AdminServer
from servers.models import Server


def public_bans(request):
    """Публичная страница со списком всех наказаний"""
    punishments = Punishment.objects.all().select_related(
        'admin', 'server', 'unbanned_by'
    ).order_by('-issued_at')

    # Фильтры
    punishment_type_filter = request.GET.get('type')
    server_filter = request.GET.get('server')
    status_filter = request.GET.get('status')

    if punishment_type_filter:
        punishments = punishments.filter(punishment_type=punishment_type_filter)

    if server_filter:
        punishments = punishments.filter(server_id=server_filter)

    if status_filter == 'active':
        punishments = punishments.filter(is_active=True)
    elif status_filter == 'inactive':
        punishments = punishments.filter(is_active=False)

    servers = Server.objects.filter(is_active=True).order_by('name')

    context = {
        'punishments': punishments,
        'servers': servers,
        'selected_type': punishment_type_filter,
        'selected_server': server_filter,
        'selected_status': status_filter,
    }
    return render(request, 'public/bans.html', context)


def public_admins(request):
    """Публичная страница со списком админов"""
    permissions = AdminServer.objects.filter(
        admin__is_active=True,
        server__is_active=True
    ).select_related('admin', 'server', 'group').order_by('server__name', '-immunity')

    # Фильтр по серверу
    server_filter = request.GET.get('server')
    if server_filter:
        permissions = permissions.filter(server_id=server_filter)

    servers = Server.objects.filter(is_active=True).order_by('name')

    context = {
        'permissions': permissions,
        'servers': servers,
        'selected_server': server_filter,
    }
    return render(request, 'public/admins.html', context)
