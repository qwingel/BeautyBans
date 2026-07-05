from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Server
import json


@csrf_exempt
@require_http_methods(["POST"])
def heartbeat(request):
    """
    Heartbeat endpoint для явной верификации сервера

    POST /api/servers/heartbeat/
    Body: {
        "server_token": "uuid-сервера"
    }

    Response: {
        "verified": true,
        "server_name": "My Server",
        "server_id": 1
    }
    """
    try:
        data = json.loads(request.body)
        server_token = data.get('server_token')

        if not server_token:
            return JsonResponse({'error': 'Missing server_token'}, status=400, json_dumps_params={'ensure_ascii': False})

        # Проверка токена сервера
        try:
            server = Server.objects.get(token=server_token, is_active=True)
        except Server.DoesNotExist:
            return JsonResponse({'error': 'Invalid server token'}, status=403, json_dumps_params={'ensure_ascii': False})

        # Верификация
        was_verified = server.is_verified
        if not was_verified:
            server.is_verified = True
            server.save(update_fields=['is_verified'])

        return JsonResponse({
            'verified': True,
            'server_name': server.name,
            'server_id': server.id,
            'was_verified': was_verified
        }, json_dumps_params={'ensure_ascii': False})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500, json_dumps_params={'ensure_ascii': False})
