# BeautyBans 🎮

Веб-система управления банами для Counter-Strike серверов (CS 1.6 и CS 2).

## 🚀 Быстрый старт с Docker

### 1. Клонировать репозиторий
```bash
git clone <your-repo-url>
cd BeautyBans
```

### 2. Настроить переменные окружения
```bash
cp .env.example .env
nano .env  # или любой редактор
```

**Важно изменить:**
- `SECRET_KEY` — случайная строка 50+ символов
- `POSTGRES_PASSWORD` — сильный пароль
- `ALLOWED_HOSTS` — ваш домен

### 3. Запустить
```bash
docker-compose up -d
```

### 4. Создать суперпользователя
```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. Готово!
Открой: `http://your-server-ip`

---

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
```

**Перезапустить:**
```bash
docker-compose restart
```

**Обновить:**
```bash
git pull
docker-compose up -d --build
```

---

## 📦 Бэкап БД

**Создать:**
```bash
docker-compose exec db pg_dump -U beautybans_user beautybans > backup.sql
```

**Восстановить:**
```bash
cat backup.sql | docker-compose exec -T db psql -U beautybans_user beautybans
```

---

## 📡 API Документация

См. [beautybans.md](beautybans.md)

---

## 🔧 Разработка без Docker

**Требования:**
- Python 3.13+
- PostgreSQL 17+

**Установка:**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows

pip install -r requirements.txt
cd beautybans
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 📝 Структура

```
BeautyBans/
├── beautybans/          # Django проект
│   ├── servers/         # Управление серверами
│   ├── admins/          # Администраторы и группы
│   ├── punishments/     # Баны, муты, гаги
│   └── beautybans/      # Настройки
├── Dockerfile           # Docker образ
├── docker-compose.yml   # Оркестрация
├── nginx.conf           # Nginx конфигурация
└── requirements.txt     # Python зависимости
```

---

## 🌐 Плагины

**CS 1.6 (AMX Mod X):**
- В разработке

**CS 2 (CounterStrikeSharp):**
- В разработке

---

## 📄 Лицензия

MIT

---

**Создано с ❤️ для CS комьюнити**
