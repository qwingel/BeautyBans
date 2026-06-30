# BeautyBans API Documentation

Документация API для разработки плагинов под CS 1.6 (AMX Mod X) и CS 2 (CounterStrikeSharp).

---

## 🔑 Аутентификация

Все API запросы требуют **server_token** (UUID) в теле запроса.

**Получение токена:**
1. Добавить сервер через веб-панель
2. Раскрыть детали сервера (клик по строке)
3. Скопировать токен кнопкой 📋

**Важно:**
- Токен уникален для каждого сервера
- При первом запросе сервер автоматически верифицируется

---

## 📡 Endpoints

### 1. Проверка прав администратора

**POST** `/admins/api/check/`

Проверяет права игрока на сервере.

**Request:**
```json
{
    "server_token": "550e8400-e29b-41d4-a716-446655440000",
    "steam_id": "STEAM_0:1:123456"
}
```

**Response (админ найден):**
```json
{
    "is_admin": true,
    "flags": "abcdefgh",
    "immunity": 100,
    "group": "Super Admin"
}
```

**Response (не админ):**
```json
{
    "is_admin": false,
    "flags": "",
    "immunity": 0,
    "group": null
}
```

**Errors:**
- `400` — Missing server_token or steam_id
- `403` — Invalid server token

---

### 2. Проверка наказаний игрока

**POST** `/punishments/api/check/`

Проверяет активные баны/муты/гаги при подключении игрока.

**Request:**
```json
{
    "server_token": "550e8400-e29b-41d4-a716-446655440000",
    "steam_id": "STEAM_0:1:123456",
    "player_ip": "127.0.0.1"
}
```

**Response:**
```json
{
    "banned": true,
    "punishments": [
        {
            "type": "ban",
            "reason": "Читы",
            "expires_at": "2026-07-01 15:30:00",
            "remaining_minutes": 120,
            "is_permanent": false
        }
    ]
}
```

**Особенности:**
- Автоматически снимает истёкшие наказания
- Проверяет IP баны (точное совпадение + подсети /24)
- `expires_at` = `null` для перманентных наказаний
- `remaining_minutes` = `null` для перманентных

**Errors:**
- `400` — Missing server_token or steam_id
- `403` — Invalid server token

---

### 3. Выдача наказания

**POST** `/punishments/api/add/`

Выдаёт бан/мут/гаг игроку.

**Request:**
```json
{
    "server_token": "550e8400-e29b-41d4-a716-446655440000",
    "admin_steam_id": "STEAM_0:1:999999",
    "target_steam_id": "STEAM_0:1:123456",
    "target_name": "Player Name",
    "target_ip": "127.0.0.1",
    "punishment_type": "ban",
    "reason": "Читы",
    "duration": 60,
    "ban_subnet": false
}
```

**Параметры:**
- `admin_steam_id` — Steam ID админа (опционально, `null` = консоль)
- `target_steam_id` — Steam ID цели (обязательно)
- `target_name` — Ник цели (обязательно)
- `target_ip` — IP цели (опционально)
- `punishment_type` — `ban` / `mute` / `gag` (обязательно)
- `reason` — Причина (обязательно)
- `duration` — Минуты (`0` = перманент, обязательно)
- `ban_subnet` — Банить подсеть /24 (опционально, по умолчанию `false`)

**Response (успех):**
```json
{
    "success": true,
    "punishment_id": 123
}
```

**Response (недостаточно иммунитета):**
```json
{
    "error": "Cannot punish this player - insufficient immunity",
    "admin_immunity": 50,
    "target_immunity": 80
}
```

**Правила иммунитета:**
- Админ может наказать цель только если `admin_immunity > target_immunity` (строго больше)
- Админы одного уровня **не могут** наказывать друг друга
- Консольные наказания (`admin_steam_id = null`) игнорируют иммунитет

**Errors:**
- `400` — Missing required fields / Invalid punishment_type
- `403` — Invalid server token / Insufficient immunity
- `404` — Admin not found or inactive

---

### 4. Снятие наказания

**POST** `/punishments/api/remove/`

Снимает активные наказания с игрока.

**Request:**
```json
{
    "server_token": "550e8400-e29b-41d4-a716-446655440000",
    "admin_steam_id": "STEAM_0:1:999999",
    "target_steam_id": "STEAM_0:1:123456",
    "punishment_type": "ban",
    "reason": "Разбанен по апелляции"
}
```

**Параметры:**
- `admin_steam_id` — Steam ID админа (опционально)
- `target_steam_id` — Steam ID цели (обязательно)
- `punishment_type` — Тип (`ban`/`mute`/`gag`, опционально — если не указан, снимает все типы)
- `reason` — Причина снятия (опционально, по умолчанию "Снято администратором")

**Response (успех):**
```json
{
    "success": true,
    "removed_count": 2
}
```

**Response (частичное снятие):**
```json
{
    "success": true,
    "removed_count": 1,
    "cannot_remove": [
        {
            "punishment_id": 123,
            "issued_by": "SuperAdmin",
            "reason": "Insufficient immunity"
        }
    ]
}
```

**Response (нет прав):**
```json
{
    "error": "Cannot remove any punishments - insufficient immunity",
    "cannot_remove": [...]
}
```

**Правила снятия:**
1. ✅ **Консольные наказания** (`admin = NULL`) — может снять любой админ
2. ✅ **Свои наказания** — админ может снять то, что сам выдал
3. ✅ **Выше иммунитет** — если `admin_immunity > issuer_immunity`
4. ✅ **Админ без прав** — если админ, выдавший наказание, потерял права на сервере

**Errors:**
- `400` — Missing server_token or target_steam_id
- `403` — Invalid server token / Cannot remove (нет прав ни на одно)
- `404` — Admin not found or inactive

---

### 5. Heartbeat (опционально)

**POST** `/servers/api/heartbeat/`

Явная верификация сервера (альтернатива автоверификации).

**Request:**
```json
{
    "server_token": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
    "verified": true,
    "server_name": "My Server",
    "server_id": 1,
    "was_verified": false
}
```

**Примечание:**
Автоверификация происходит при любом API запросе, heartbeat нужен только для явной верификации при старте плагина.

---

## 🛠️ Рекомендации для плагинов

### При загрузке плагина:
1. Загрузить `server_token` из конфига
2. (Опционально) Вызвать `/api/servers/heartbeat/` для проверки

### При подключении игрока:
1. Вызвать `/api/punishments/check/` с `steam_id` и `player_ip`
2. Если `banned = true` → кикнуть игрока с причиной
3. Применить муты/гаги из массива `punishments`

### При загрузке админов:
1. Вызвать `/api/admins/check/` для каждого игрока на сервере
2. Установить флаги и иммунитет

### Команды бана:
1. Проверить права админа (`/api/admins/check/`)
2. Вызвать `/api/punishments/add/`
3. Обработать ответ (успех / недостаточно иммунитета)
4. Кикнуть цель если это бан

### Команды разбана:
1. Вызвать `/api/punishments/remove/`
2. Обработать `cannot_remove` если есть

---

## 🔒 Безопасность

- ✅ Все endpoints используют POST
- ✅ CSRF exempt (для API)
- ✅ Токен проверяется в БД
- ✅ Неактивные серверы не могут использовать API
- ✅ Иммунитет защищает от абуза

---

## 📝 Примеры ошибок

**400 Bad Request:**
```json
{
    "error": "Missing server_token or steam_id"
}
```

**403 Forbidden:**
```json
{
    "error": "Invalid server token"
}
```

**500 Internal Server Error:**
```json
{
    "error": "Database connection failed"
}
```

---

## 🌐 URL структура

**Базовый URL:** `http://your-domain.com/`

**Полные пути:**
- `http://your-domain.com/admins/api/check/`
- `http://your-domain.com/punishments/api/check/`
- `http://your-domain.com/punishments/api/add/`
- `http://your-domain.com/punishments/api/remove/`
- `http://your-domain.com/servers/api/heartbeat/`

---

## 💡 Tips

1. **Кэшируйте права админов** — не проверяйте при каждой команде
2. **Обновляйте кэш** — при входе/выходе админа
3. **Обрабатывайте таймауты** — API может быть недоступен
4. **Логируйте ошибки** — для отладки
5. **Steam ID формат** — используйте `STEAM_0:X:XXXXXX`

---

**Готово к разработке плагинов!** 🎮
