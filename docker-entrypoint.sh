#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h db -p 5432 -U $POSTGRES_USER > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL started"

echo "Creating static directories..."
mkdir -p /app/staticfiles /app/media
chmod -R 755 /app/staticfiles /app/media

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Setting up cron for auto-expiring punishments..."
# Создаём crontab файл
echo "*/5 * * * * cd /app && /usr/local/bin/python manage.py expire_punishments >> /var/log/cron.log 2>&1" > /etc/cron.d/beautybans
chmod 0644 /etc/cron.d/beautybans
crontab /etc/cron.d/beautybans
touch /var/log/cron.log

# Запускаем cron в фоне
cron

echo "Starting application..."
exec "$@"
