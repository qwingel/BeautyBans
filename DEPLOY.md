# 🚀 Инструкция по деплою BeautyBans на VDS

## 📋 Требования

- VDS с Ubuntu 20.04+ / Debian 11+
- Docker + Docker Compose
- Минимум: 1 GB RAM, 10 GB диск
- Открытые порты: 80 (HTTP), 443 (HTTPS - опционально)

---

## 🔧 Установка на VDS

### 1. Подключиться к VDS
```bash
ssh root@your-server-ip
```

### 2. Установить Docker
```bash
# Обновить пакеты
apt update && apt upgrade -y

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установить Docker Compose
apt install docker-compose-plugin -y

# Проверить установку
docker --version
docker compose version
```

### 3. Клонировать проект
```bash
cd /opt
git clone <your-repo-url> beautybans
cd beautybans
```

### 4. Настроить .env
```bash
cp .env.example .env
nano .env
```

**Обязательно изменить:**
```env
DEBUG=False
SECRET_KEY=СГЕНЕРИРУЙ_СЛУЧАЙНУЮ_СТРОКУ_50_СИМВОЛОВ
ALLOWED_HOSTS=your-domain.com,your-server-ip
POSTGRES_PASSWORD=СИЛЬНЫЙ_ПАРОЛЬ_ДЛЯ_БД
HTTP_PORT=80
```

**Генерация SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 5. Запустить контейнеры
```bash
docker compose up -d
```

### 6. Создать суперпользователя
```bash
docker compose exec web python manage.py createsuperuser
```

Введи:
- Username: `admin`
- Email: `admin@example.com`
- Password: **СЛОЖНЫЙ ПАРОЛЬ**

### 7. Проверить
Открой в браузере: `http://your-server-ip`

---

## 🔒 HTTPS (Let's Encrypt)

### 1. Установить Certbot
```bash
apt install certbot python3-certbot-nginx -y
```

### 2. Остановить Nginx в Docker
```bash
docker compose stop nginx
```

### 3. Получить сертификат
```bash
certbot certonly --standalone -d your-domain.com
```

### 4. Обновить nginx.conf
Добавь в `nginx.conf`:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # ... остальная конфигурация
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 5. Обновить docker-compose.yml
```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
  ports:
    - "80:80"
    - "443:443"
```

### 6. Перезапустить
```bash
docker compose up -d --build
```

---

## 📦 Бэкапы

### Автоматический бэкап БД (cron)
```bash
# Создать скрипт
nano /opt/backup-beautybans.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/beautybans-backups"
DATE=$(date +%Y-%m-%d_%H-%M)
mkdir -p $BACKUP_DIR

docker compose exec -T db pg_dump -U beautybans_user beautybans > $BACKUP_DIR/backup_$DATE.sql

# Удалить старые (>7 дней)
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

```bash
chmod +x /opt/backup-beautybans.sh
```

**Добавить в cron (ежедневно в 3:00):**
```bash
crontab -e
```

Добавить строку:
```
0 3 * * * /opt/backup-beautybans.sh
```

---

## 🔄 Обновление

```bash
cd /opt/beautybans
git pull
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose restart
```

---

## 📊 Мониторинг

**Логи:**
```bash
docker compose logs -f web
docker compose logs -f db
docker compose logs -f nginx
```

**Статус:**
```bash
docker compose ps
```

**Использование ресурсов:**
```bash
docker stats
```

---

## 🆘 Troubleshooting

### Проблема: контейнеры не запускаются
```bash
docker compose logs
```

### Проблема: ошибка подключения к БД
```bash
docker compose exec web python manage.py check --database default
```

### Проблема: статика не загружается
```bash
docker compose exec web python manage.py collectstatic --noinput
docker compose restart nginx
```

### Полная переустановка
```bash
docker compose down -v  # УДАЛИТ ВСЕ ДАННЫЕ!
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

---

## 🔐 Безопасность

1. **Фаервол:**
```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

2. **Изменить SSH порт** (в `/etc/ssh/sshd_config`)

3. **Отключить root login по SSH**

4. **Регулярно обновлять:**
```bash
apt update && apt upgrade -y
docker compose pull
docker compose up -d
```

---

**Готово! BeautyBans работает на VDS** 🎉
