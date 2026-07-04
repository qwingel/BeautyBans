# BeautyBans 🎮

Веб-система управления банами и администрацией для Counter-Strike серверов

## ✨ Возможности

- 🔨 **Управление наказаниями** — баны, муты, гаги
- 👥 **Система администраторов** — группы, флаги, иммунитет
- 🔌 **REST API** — для плагинов CS 1.6 / CS 2


## 🚀 Быстрый старт

### Требования
- Docker + Docker Compose
- 1GB RAM / 10GB диск

### Установка

#### 1. Клонировать репозиторий
```bash
git clone https://github.com/qwingel/BeautyBans.git
cd BeautyBans
```

#### 2. Настроить окружение
```bash
cp .env.example .env
nano .env
```

**Обязательно измените:**
```env
DEBUG=False
SECRET_KEY=ваш_случайный_ключ
POSTGRES_PASSWORD=пароль_для_БД
ALLOWED_HOSTS=your-domain.com,123.45.67.89
URL_PREFIX=
```

**Генерация SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---
### Настройка URL
### Вариант 1: Корневой домен

**URL структура:**
- `http://your-domain.com/` — главная
- `http://your-domain.com/banlist/` - банлист
- `http://your-domain.com/admins/` — список админов
- `http://your-domain.com/adminpanel/` — вход в админ-панель

### Вариант 2: Подкаталог
**Настройка `.env`:**
```env
URL_PREFIX=/beautybans
```

**URL структура:**
- `http://your-domain.com/beautybans/` — главная
- `http://your-domain.com/beautybans/banlist/` — банлист
- `http://your-domain.com/beautybans/admins/` — список админов
- `http://your-domain.com/beautybans/adminpanel/` — вход в админ-панель

**Nginx конфигурация для подкаталога:**
```nginx
location /beautybans/ {
    proxy_pass http://localhost:8000/beautybans/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```


#### 3. Запустить
```bash
docker-compose up -d
```


#### 4. Создать администратора
```bash
docker-compose exec web python manage.py createsuperuser
```


#### 5. Готово! 🎉
Откройте браузер и перейдите на ваш сайт



## 🛠️ Управление

**Запустить:**
```bash
docker-compose up -d
```

**Остановить:**
```bash
docker-compose down
```

**Посмотреть логи:**
```bash
docker-compose logs -f web
docker-compose logs -f db
```

**Перезапустить:**
```bash
docker-compose restart
```

**Обновить до новой версии:**
```bash
git pull
docker-compose up -d --build
docker-compose exec web python manage.py migrate
```

## 📡 API для плагинов

### Endpoints

**Проверка прав администратора:**
```http
POST /adminpanel/administration/api/check/
Content-Type: application/json

{
    "server_token": "uuid-сервера",
    "steam_id": "STEAM_0:1:123456"
}
```

**Проверка наказаний игрока:**
```http
POST /adminpanel/punishments/api/check/
Content-Type: application/json

{
    "server_token": "uuid-сервера",
    "steam_id": "STEAM_0:1:123456",
    "player_ip": "127.0.0.1"
}
```

**Выдача наказания:**
```http
POST /adminpanel/punishments/api/add/
Content-Type: application/json

{
    "server_token": "uuid-сервера",
    "admin_steam_id": "STEAM_0:1:999999",
    "target_steam_id": "STEAM_0:1:123456",
    "target_name": "Player Name",
    "target_ip": "127.0.0.1",
    "punishment_type": "ban",
    "reason": "Читы",
    "duration": 0,
    "ban_subnet": false
}
```

**Снятие наказания:**
```http
POST /adminpanel/punishments/api/remove/
Content-Type: application/json

{
    "server_token": "uuid-сервера",
    "admin_steam_id": "STEAM_0:1:999999",
    "target_steam_id": "STEAM_0:1:123456",
    "punishment_type": "ban",
    "reason": "Ошибка"
}
```

Подробная документация: [beautybans.md](beautybans.md)

## 📁 Структура проекта

```
BeautyBans/
├── beautybans/                 # Django проект
│   ├── beautybans/             # Настройки проекта
│   │   ├── settings.py         # Конфигурация Django
│   │   ├── urls.py             # Маршрутизация URL
│   │   └── public_views.py     # Публичные страницы
│   ├── servers/                # Управление серверами
│   │   ├── models.py           # Модель Server
│   │   ├── views.py            # CRUD серверов
│   │   └── api.py              # API heartbeat
│   ├── admins/                 # Администраторы
│   │   ├── models.py           # Admin, AdminGroup, AdminServer
│   │   ├── views.py            # Управление админами
│   │   └── api.py              # API проверки прав
│   ├── punishments/            # Наказания
│   │   ├── models.py           # Punishment
│   │   ├── views.py            # Управление наказаниями
│   │   └── api.py              # API банов/мутов
│   └── templates/              # HTML шаблоны
├── Dockerfile                  # Docker образ приложения
├── docker-compose.yml          # Оркестрация контейнеров
├── nginx.conf                  # Конфигурация Nginx
├── requirements.txt            # Python зависимости
├── .env.example                # Пример конфигурации
└── README.md                   # Документация
```

## 🌐 Плагины

### CS 1.6 (AMX Mod X)
🔜 В разработке

### CS 2 (CounterStrikeSharp)
🔜 В разработке

---

**Создано с ❤️ для CS комьюнити**
