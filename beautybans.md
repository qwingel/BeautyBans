# BeautyBans API Documentation

Документация API для разработки плагинов Counter-Strike 1.6 и CS2

## 🔑 Аутентификация

Все API запросы требуют **server_token** (UUID) в теле запроса.

**Получение токена:**
1. Добавить сервер через веб-панель (`/adminpanel/servers/`)
2. Клик по серверу → скопировать токен

## 📡 Endpoints

### 1. Проверка прав администратора

**POST** `/adminpanel/administration/api/check/`

Проверяет права игрока на сервере.

**Request:**
```json
{
    "server_token": "123a4567-b89c-01d2-e345-446655440000",
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

**POST** `/adminpanel/punishments/api/check/`

Проверяет активные баны/муты/гаги игрока при подключении

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
- `expires_at` = `null` для перманентных наказаний
- `remaining_minutes` = `null` для перманентных

**Errors:**
- `400` — Missing server_token or steam_id
- `403` — Invalid server token

---

### 3. Выдача наказания

**POST** `/adminpanel/punishments/api/add/`

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

**POST** `/adminpanel/punishments/api/remove/`

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
1. **Запрос от консоли сервера** (без `admin_steam_id`) — может снять любое наказание
2. **Свои наказания** — админ может снять то, что сам выдал
3. **Выше иммунитет** — если `admin_immunity > issuer_immunity`
4. **Консольные наказания** (`admin = NULL`) — только админ с иммунитетом `>= 90`

**Errors:**
- `400` — Missing server_token or target_steam_id
- `403` — Invalid server token / Cannot remove (нет прав ни на одно)
- `404` — Admin not found or inactive

---

### 5. Heartbeat (опционально)

**POST** `/adminpanel/servers/api/heartbeat/`

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
Автоверификация происходит при любом API запросе, heartbeat нужен только для явной верификации

---

### 6. Получение списка наказаний

**POST** `/adminpanel/punishments/api/list/`

Получение списка наказаний по фильтрам

**Request:**
```json
{
    "server_token": "550e8400-e29b-41d4-a716-446655440000",
    "punishment_type": "ban",
    "is_active": true
}
```

**Параметры:**
- `server_token` — UUID сервера (обязательно, определяет какой сервер делает запрос)
- `punishment_type` — `ban`, `mute`, `gag`, `all` (опционально, по умолчанию `all`)
- `is_active` — `true` = активные, `false` = снятые, `null` = все (опционально, по умолчанию `true`)

**Response:**
```json
{
    "success": true,
    "count": 15,
    "punishments": [
        {
            "id": 123,
            "type": "ban",
            "target_steam_id": "STEAM_0:1:123456",
            "target_name": "Player",
            "target_ip": "127.0.0.1",
            "ban_subnet": false,
            "reason": "Читы",
            "issued_at": "2026-07-05 15:00:00",
            "expires_at": "2026-07-05 18:00:00",
            "duration": 180,
            "is_permanent": false,
            "is_active": true,
            "admin": "AdminName",
            "admin_steam_id": "STEAM_0:1:999999",
            "server": "My Server",
            "unbanned_by": null,
            "unban_reason": ""
        }
    ]
}
```

**Примеры использования:**

1. **Все активные баны текущего сервера**:
```json
{
    "server_token": "...",
    "punishment_type": "ban"
}
```

2. **Все снятые муты текущего сервера**:
```json
{
    "server_token": "...",
    "punishment_type": "mute",
    "is_active": false
}
```

3. **Все наказания текущего сервера (активные и снятые)**:
```json
{
    "server_token": "...",
    "is_active": null
}
```

**Errors:**
- `400` — Missing server_token / Invalid punishment_type
- `403` — Invalid server token

---

### 7. Поиск наказаний

**POST** `/adminpanel/punishments/api/search/`

Поиск активных наказаний по нику/Steam ID

**Request:**
```json
{
    "server_token": "550e8400-e29b-41d4-a716-446655440000",
    "admin_steam_id": "STEAM_0:1:999999",
    "punishment_type": "ban",
    "search_query": "Player123",
    "from_server": true
}
```

**Параметры:**
- `server_token` — UUID сервера (обязательно)
- `admin_steam_id` — Steam ID админа (обязательно, для проверки прав)
- `punishment_type` — `ban`, `mute`, `gag`, `all` (по умолчанию `all`)
- `search_query` — Ник или Steam ID (регистр не важен, обязательно)
- `from_server` — от сервера ли поступает запрос. `true` = лимит 20 записей, `false` = все (опционально, по умолчанию `false`)

**Response:**
```json
{
    "success": true,
    "count": 3,
    "can_unban_count": 2,
    "punishments": [
        {
            "id": 123,
            "type": "ban",
            "target_steam_id": "STEAM_0:1:123456",
            "target_name": "Player123",
            "target_ip": "127.0.0.1",
            "ban_subnet": false,
            "reason": "Читы",
            "issued_at": "2026-07-05 15:00:00",
            "expires_at": "2026-07-05 18:00:00",
            "duration": 180,
            "is_permanent": false,
            "admin": "AdminName",
            "admin_steam_id": "STEAM_0:1:654321",
            "server": "My Server",
            "can_unban": true,
            "unban_reason": "Выдал сам"
        },
        {
            "id": 124,
            "type": "ban",
            "target_steam_id": "STEAM_0:1:123456",
            "target_name": "Player123",
            "target_ip": null,
            "ban_subnet": false,
            "reason": "WallHack",
            "issued_at": "2026-07-04 10:00:00",
            "expires_at": null,
            "duration": 0,
            "is_permanent": true,
            "admin": "SuperAdmin",
            "admin_steam_id": "STEAM_0:1:111111",
            "server": "My Server",
            "can_unban": false,
            "unban_reason": ""
        }
    ]
}
```

**Errors:**
- `400` — Missing required fields / Invalid punishment_type
- `403` — Invalid server token / Admin has no permissions / Admin permissions expired
- `404` — Admin not found


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