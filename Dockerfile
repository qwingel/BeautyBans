# BeautyBans Dockerfile
FROM python:3.13-slim

# Рабочая директория
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY beautybans/ /app/

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 beautybans && chown -R beautybans:beautybans /app

# Создаем директории для volumes и даем права
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R beautybans:beautybans /app/staticfiles /app/media

USER beautybans

# Порт Django
EXPOSE 8000

# Entrypoint для миграций
COPY --chown=beautybans:beautybans docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "beautybans.wsgi:application"]
