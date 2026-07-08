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
python manage.py collectstatic --noinput

echo "Setting up cron for auto-expiring..."

# Сохраняем все переменные окружения в файл (для cron)
printenv > /app/.env.runtime

# Создаём crontab файл с двумя задачами
cat > /etc/cron.d/beautybans << 'EOF'
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

*/5 * * * * root bash -c 'set -a && source /app/.env.runtime && cd /app && python manage.py expire_punishments' >> /var/log/cron.log 2>&1
*/5 * * * * root bash -c 'set -a && source /app/.env.runtime && cd /app && python manage.py expire_admin_permissions' >> /var/log/cron.log 2>&1
EOF

chmod 0644 /etc/cron.d/beautybans
crontab /etc/cron.d/beautybans
touch /var/log/cron.log

# Запускаем cron в фоне
cron

echo "Starting application..."
exec "$@"
