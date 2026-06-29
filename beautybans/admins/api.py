from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Admin, AdminServer
from servers.models import Server
import json


@csrf_exempt
@require_http_methods(["POST"])
def check_admin(request):
    """
    API для проверки прав администратора на сервере

    POST /api/admins/check/
    Body: {
        "server_token": "uuid-сервера",
        "steam_id": "STEAM_0:1:123456"
    }

    Response: {
        "is_admin": true,
        "flags": "abcdefgh",
        "immunity": 100,
        "group": "Super Admin" или null
    }
    """
    try:
        data = json.loads(request.body)
        server_token = data.get('server_token')
        steam_id = data.get('steam_id')

        if not server_token or not steam_id:
            return JsonResponse({'error': 'Missing server_token or steam_id'}, status=400)

        # Проверка токена сервера
        try:
            server = Server.objects.get(token=server_token, is_active=True)
        except Server.DoesNotExist:
            return JsonResponse({'error': 'Invalid server token'}, status=403)

        # Поиск админа
        try:
            admin = Admin.objects.get(steam_id=steam_id, is_active=True)
        except Admin.DoesNotExist:
            return JsonResponse({
                'is_admin': False,
                'flags': '',
                'immunity': 0,
                'group': None
            })

        # Поиск прав на этом сервере
        try:
            permission = AdminServer.objects.select_related('group').get(
                admin=admin,
                server=server
            )

            return JsonResponse({
                'is_admin': True,
                'flags': permission.get_effective_flags(),
                'immunity': permission.get_effective_immunity(),
                'group': permission.group.name if permission.group else None
            })

        except AdminServer.DoesNotExist:
            # Админ существует, но нет прав на этом сервере
            return JsonResponse({
                'is_admin': False,
                'flags': '',
                'immunity': 0,
                'group': None
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
