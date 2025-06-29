#!/bin/bash

wait_for_postgres() {
  until pg_isready -h postgres -U app; do
    echo "Ожидание доступа к базе данных PostgreSQL..."
    sleep 2
  done
  echo "Подключение к базе данных PostgreSQL установлено..."
}

wait_for_postgres

echo "База данных доступна..."

python manage.py collectstatic --no-input

echo "Удаление миграций для приложений admin и users из таблицы django_migrations..."
python manage.py shell -c "from django.db import connection; cursor = connection.cursor(); cursor.execute(\"DELETE FROM django_migrations WHERE app IN ('admin', 'users')\"); cursor.close()"

echo "Создание миграций для приложения users..."
python manage.py makemigrations users

echo "Применение миграций для приложения users..."
python manage.py migrate users

echo "Применение миграций для других приложений..."
python manage.py migrate movies --fake-initial

echo "Создание суперпользователя..."
python manage.py createsuperuser --noinput || true

echo "Применение миграций для других приложений..."
python manage.py migrate movies --fake-initial

echo "Создание суперпользователя..."
python manage.py createsuperuser --noinput || true

echo "Запуск приложения с помощью uWSGI..."
uwsgi --strict --ini uwsgi.ini