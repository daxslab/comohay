#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$RESET_DATABASE" = "true" ]
then
  echo "Resting database..."
  python manage.py reset_db -c --noinput
fi

python manage.py migrate
python manage.py compilemessages

exec "$@"