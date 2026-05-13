#!/bin/sh
echo "🚀 Запуск entrypoint скрипта..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn zd.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --access-logfile - \
  --error-logfile -