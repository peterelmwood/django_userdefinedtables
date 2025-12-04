#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
while ! python manage.py check --database default 2>/dev/null; do
  sleep 1
done
echo "Database is ready!"

python manage.py migrate

python manage.py runserver 0.0.0.0:8000
