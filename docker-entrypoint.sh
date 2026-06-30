#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h db -p 5432 -U $POSTGRES_USER > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL started"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting application..."
exec "$@"
