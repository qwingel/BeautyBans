from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Punishment
from servers.models import Server
from servers.utils import verify_server_if_needed
import json


@csrf_exempt
@require_http_methods(["POST"])
def check_player(request):
    """
    API для проверки наказаний игрока при подключении к серверу

    POST /api/punishments/check/
    Body: {
        "server_token": "uuid-сервера",
        "steam_id": "STEAM_0:1:123456",
        "player_ip": "127.0.0.1"
    }

    Response: {
        "banned": true/false,
        "punishments": [
            {
                "type": "ban",
                "reason": "Причина",
                "expires_at": "2026-06-30 23:00:00" или null (если перманент),
                "remaining_minutes": 120 или null
            }
        ]
    }
    """
    try:
        data = json.loads(request.body)
        server_token = data.get('server_token')
        steam_id = data.get('steam_id')
        player_ip = data.get('player_ip')

        if not server_token or not steam_id:
            return JsonResponse({'error': 'Missing server_token or steam_id'}, status=400, json_dumps_params={'ensure_ascii': False})

        # Проверка токена сервера
        try:
            server = Server.objects.get(token=server_token, is_active=True)
            # Автоверификация при первом запросе
            verify_server_if_needed(server)
        except Server.DoesNotExist:
            return JsonResponse({'error': 'Invalid server token'}, status=403, json_dumps_params={'ensure_ascii': False})

        # Получаем активные наказания
        punishments = Punishment.objects.filter(
            target_steam_id=steam_id,
            is_active=True
        ).select_related('server')

        # Автоснятие истёкших наказаний
        for punishment in punishments:
            punishment.auto_expire()

        # Перезагружаем список активных наказаний после автоснятия
        active_punishments = Punishment.objects.filter(
            target_steam_id=steam_id,
            is_active=True
        )

        # Проверка IP бана
        if player_ip:
            ip_punishments = Punishment.objects.filter(
                target_ip__isnull=False,
                is_active=True,
                punishment_type='ban'
            )

            for ip_ban in ip_punishments:
                ip_ban.auto_expire()
                if ip_ban.is_active:
                    if ip_ban.ban_subnet:
                        # Проверка по подсети (первые 3 октета)
                        player_subnet = '.'.join(player_ip.split('.')[:3])
                        ban_subnet = '.'.join(ip_ban.target_ip.split('.')[:3])
                        if player_subnet == ban_subnet:
                            active_punishments = active_punishments | Punishment.objects.filter(pk=ip_ban.pk)
                    else:
                        # Точное совпадение IP
                        if ip_ban.target_ip == player_ip:
                            active_punishments = active_punishments | Punishment.objects.filter(pk=ip_ban.pk)

        # Формируем ответ
        punishments_list = []
        has_ban = False

        for punishment in active_punishments.distinct():
            time_remaining = punishment.get_time_remaining()

            # Конвертируем в локальное время (Europe/Moscow)
            expires_at_local = None
            if punishment.expires_at:
                expires_at_local = timezone.localtime(punishment.expires_at).strftime('%Y-%m-%d %H:%M:%S')

            punishments_list.append({
                'type': punishment.punishment_type,
                'reason': punishment.reason,
                'expires_at': expires_at_local,
                'remaining_minutes': int(time_remaining.total_seconds() / 60) if time_remaining else None,
                'is_permanent': punishment.duration == 0
            })

            if punishment.punishment_type == 'ban':
                has_ban = True

        return JsonResponse({
            'banned': has_ban,
            'punishments': punishments_list
        }, json_dumps_params={'ensure_ascii': False})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
@require_http_methods(["POST"])
def add_punishment(request):
    """
    API для выдачи наказания с сервера

    POST /api/punishments/add/
    Body: {
        "server_token": "uuid-сервера",
        "admin_steam_id": "STEAM_0:1:999999",  // опционально, если NULL - консольное наказание
        "target_steam_id": "STEAM_0:1:123456",
        "target_name": "Player Name",
        "target_ip": "127.0.0.1",  // опционально
        "punishment_type": "ban",  // ban/mute/gag
        "reason": "Причина наказания",
        "duration": 60,  // минуты, 0 = перманент
        "ban_subnet": false  // опционально, по умолчанию false
    }

    Response: {
        "success": true,
        "punishment_id": 123
    }
    """
    try:
        data = json.loads(request.body)
        server_token = data.get('server_token')
        admin_steam_id = data.get('admin_steam_id')
        target_steam_id = data.get('target_steam_id')
        target_name = data.get('target_name')
        target_ip = data.get('target_ip')
        punishment_type = data.get('punishment_type')
        reason = data.get('reason')
        duration = data.get('duration', 0)
        ban_subnet = data.get('ban_subnet', False)

        # Валидация обязательных полей
        if not all([server_token, target_steam_id, target_name, punishment_type, reason]):
            return JsonResponse({'error': 'Missing required fields'}, status=400, json_dumps_params={'ensure_ascii': False})

        # Проверка токена сервера
        try:
            server = Server.objects.get(token=server_token, is_active=True)
            # Автоверификация при первом запросе
            verify_server_if_needed(server)
        except Server.DoesNotExist:
            return JsonResponse({'error': 'Invalid server token'}, status=403, json_dumps_params={'ensure_ascii': False})

        # Проверка типа наказания
        valid_types = ['ban', 'mute', 'gag']
        if punishment_type not in valid_types:
            return JsonResponse({'error': f'Invalid punishment_type. Must be one of: {valid_types}'}, status=400, json_dumps_params={'ensure_ascii': False})

        # Поиск админа (если указан)
        admin = None
        admin_immunity = 0
        if admin_steam_id:
            try:
                from admins.models import Admin, AdminServer
                admin = Admin.objects.get(steam_id=admin_steam_id, is_active=True)

                # Получаем иммунитет админа на этом сервере
                try:
                    admin_perm = AdminServer.objects.select_related('group').get(admin=admin, server=server)
                    admin_immunity = admin_perm.get_effective_immunity()
                except AdminServer.DoesNotExist:
                    admin_immunity = 0
            except Admin.DoesNotExist:
                return JsonResponse({'error': 'Admin not found or inactive'}, status=404, json_dumps_params={'ensure_ascii': False})

        # Проверка иммунитета цели (если цель тоже админ)
        try:
            from admins.models import Admin, AdminServer
            target_admin = Admin.objects.get(steam_id=target_steam_id, is_active=True)

            # Проверяем права цели на этом сервере
            try:
                target_perm = AdminServer.objects.select_related('group').get(admin=target_admin, server=server)
                target_immunity = target_perm.get_effective_immunity()

                # Проверка: иммунитет админа должен быть строго больше
                if admin_immunity <= target_immunity:
                    return JsonResponse({
                        'error': 'Cannot punish this player - insufficient immunity',
                        'admin_immunity': admin_immunity,
                        'target_immunity': target_immunity
                    }, status=403, json_dumps_params={'ensure_ascii': False})
            except AdminServer.DoesNotExist:
                # Цель админ, но нет прав на этом сервере - можно наказывать
                pass
        except Admin.DoesNotExist:
            # Цель не админ - можно наказывать
            pass

        # Создание наказания
        punishment = Punishment.objects.create(
            punishment_type=punishment_type,
            target_steam_id=target_steam_id,
            target_name=target_name,
            target_ip=target_ip,
            ban_subnet=ban_subnet,
            reason=reason,
            admin=admin,
            server=server,
            duration=duration
        )

        return JsonResponse({
            'success': True,
            'punishment_id': punishment.id
        }, json_dumps_params={'ensure_ascii': False})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
@require_http_methods(["POST"])
def remove_punishment(request):
    """
    API для снятия наказания с сервера

    POST /api/punishments/remove/
    Body: {
        "server_token": "uuid-сервера",
        "admin_steam_id": "STEAM_0:1:999999",  // опционально
        "target_steam_id": "STEAM_0:1:123456",
        "punishment_type": "ban",  // опционально, если не указан - снимает все типы
        "reason": "Причина снятия"
    }

    Response: {
        "success": true,
        "removed_count": 2
    }
    """
    try:
        data = json.loads(request.body)
        server_token = data.get('server_token')
        admin_steam_id = data.get('admin_steam_id')
        target_steam_id = data.get('target_steam_id')
        punishment_type = data.get('punishment_type')
        reason = data.get('reason', 'Снято администратором')

        # Валидация
        if not all([server_token, target_steam_id]):
            return JsonResponse({'error': 'Missing server_token or target_steam_id'}, status=400, json_dumps_params={'ensure_ascii': False})

        # Проверка токена сервера
        try:
            server = Server.objects.get(token=server_token, is_active=True)
            # Автоверификация при первом запросе
            verify_server_if_needed(server)
        except Server.DoesNotExist:
            return JsonResponse({'error': 'Invalid server token'}, status=403, json_dumps_params={'ensure_ascii': False})

        # Поиск админа (если указан)
        admin = None
        admin_immunity = 0
        if admin_steam_id:
            try:
                from admins.models import Admin, AdminServer
                admin = Admin.objects.get(steam_id=admin_steam_id, is_active=True)

                # Получаем иммунитет админа на этом сервере
                try:
                    admin_perm = AdminServer.objects.select_related('group').get(admin=admin, server=server)
                    admin_immunity = admin_perm.get_effective_immunity()
                except AdminServer.DoesNotExist:
                    admin_immunity = 0
            except Admin.DoesNotExist:
                return JsonResponse({'error': 'Admin not found or inactive'}, status=404, json_dumps_params={'ensure_ascii': False})

        # Поиск активных наказаний
        punishments = Punishment.objects.filter(
            target_steam_id=target_steam_id,
            is_active=True
        ).select_related('admin')

        # Фильтр по типу (если указан)
        if punishment_type:
            punishments = punishments.filter(punishment_type=punishment_type)

        # Снятие наказаний с проверкой прав
        removed_count = 0
        cannot_remove = []

        for punishment in punishments:
            # Проверка прав на снятие
            can_remove = False

            # 1. Консольное наказание (admin = NULL) - может снять любой админ
            if not punishment.admin:
                can_remove = True

            # 2. Админ снимает свой собственный бан
            elif admin and punishment.admin.id == admin.id:
                can_remove = True

            # 3. Админ с иммунитетом выше того, кто выдал
            elif admin and punishment.admin:
                try:
                    from admins.models import AdminServer
                    # Получаем иммунитет админа, который выдал наказание
                    issuer_perm = AdminServer.objects.select_related('group').get(
                        admin=punishment.admin,
                        server=server
                    )
                    issuer_immunity = issuer_perm.get_effective_immunity()

                    # Проверка: иммунитет должен быть строго выше
                    if admin_immunity > issuer_immunity:
                        can_remove = True
                except AdminServer.DoesNotExist:
                    # Админ, выдавший наказание, больше не имеет прав на сервере
                    # Разрешаем снять
                    can_remove = True

            # Снимаем наказание если есть права
            if can_remove:
                punishment.is_active = False
                punishment.unbanned_by = admin
                punishment.unban_reason = reason
                punishment.save()
                removed_count += 1
            else:
                cannot_remove.append({
                    'punishment_id': punishment.id,
                    'issued_by': punishment.admin.name if punishment.admin else 'Console',
                    'reason': 'Insufficient immunity'
                })

        # Формируем ответ
        response = {
            'success': True,
            'removed_count': removed_count
        }

        if cannot_remove:
            response['cannot_remove'] = cannot_remove

        if removed_count == 0 and cannot_remove:
            return JsonResponse({
                'error': 'Cannot remove any punishments - insufficient immunity',
                'cannot_remove': cannot_remove
            }, status=403, json_dumps_params={'ensure_ascii': False})

        return JsonResponse(response, json_dumps_params={'ensure_ascii': False})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
@require_http_methods(["POST"])
def get_active_punishments(request):
    """
    API для получения списка активных наказаний по типу

    POST /adminpanel/punishments/api/list/
    Body: {
        "server_token": "uuid-сервера",
        "punishment_type": "ban"  // ban, mute, gag или null для всех
    }

    Response: {
        "success": true,
        "count": 5,
        "punishments": [
            {
                "id": 123,
                "target_steam_id": "STEAM_0:1:123456",
                "target_name": "Player",
                "target_ip": "127.0.0.1",
                "reason": "Читы",
                "issued_at": "2026-07-05 15:00:00",
                "expires_at": "2026-07-05 18:00:00",
                "duration": 60,
                "is_permanent": false,
                "admin": "AdminName",
                "server": "ServerName"
            }
        ]
    }
    """
    try:
        data = json.loads(request.body)
        server_token = data.get('server_token')
        punishment_type = data.get('punishment_type')  # Опционально

        # Валидация
        if not server_token:
            return JsonResponse({'error': 'Missing server_token'}, status=400, json_dumps_params={'ensure_ascii': False})

        # Проверка токена сервера
        try:
            server = Server.objects.get(token=server_token, is_active=True)
            verify_server_if_needed(server)
        except Server.DoesNotExist:
            return JsonResponse({'error': 'Invalid server token'}, status=403, json_dumps_params={'ensure_ascii': False})

        # Проверка типа наказания (если указан)
        if punishment_type:
            valid_types = ['ban', 'mute', 'gag']
            if punishment_type not in valid_types:
                return JsonResponse({
                    'error': f'Invalid punishment_type. Must be one of: {valid_types}'
                }, status=400, json_dumps_params={'ensure_ascii': False})

        # Получаем активные наказания
        punishments = Punishment.objects.filter(
            is_active=True,
            server=server
        ).select_related('admin', 'server')

        # Фильтр по типу (если указан)
        if punishment_type:
            punishments = punishments.filter(punishment_type=punishment_type)

        # Автоснятие истёкших
        for punishment in punishments:
            punishment.auto_expire()

        # Перезагружаем после автоснятия
        punishments = punishments.filter(is_active=True).order_by('-issued_at')

        # Формируем список
        punishments_list = []
        for punishment in punishments:
            # Конвертируем время в локальное
            issued_at_local = timezone.localtime(punishment.issued_at).strftime('%Y-%m-%d %H:%M:%S')
            expires_at_local = None
            if punishment.expires_at:
                expires_at_local = timezone.localtime(punishment.expires_at).strftime('%Y-%m-%d %H:%M:%S')

            punishments_list.append({
                'id': punishment.id,
                'type': punishment.punishment_type,
                'target_steam_id': punishment.target_steam_id,
                'target_name': punishment.target_name,
                'target_ip': punishment.target_ip,
                'ban_subnet': punishment.ban_subnet,
                'reason': punishment.reason,
                'issued_at': issued_at_local,
                'expires_at': expires_at_local,
                'duration': punishment.duration,
                'is_permanent': punishment.duration == 0,
                'admin': punishment.admin.name if punishment.admin else 'Консоль',
                'server': punishment.server.name
            })

        return JsonResponse({
            'success': True,
            'count': len(punishments_list),
            'punishments': punishments_list
        }, json_dumps_params={'ensure_ascii': False})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500, json_dumps_params={'ensure_ascii': False})
