#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
MAX_RETRIES=30
RETRY_COUNT=0

# Use a small Python script to check database connection without exposing credentials in process list
until python << END
import psycopg2
import os
try:
    psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'db'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        dbname=os.environ.get('POSTGRES_NAME')
    )
    exit(0)
except Exception:
    exit(1)
END
do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "Database did not become ready after $MAX_RETRIES seconds. Exiting."
    exit 1
  fi
  echo "Database not ready yet, retrying... ($RETRY_COUNT/$MAX_RETRIES)"
  sleep 1
done

echo "Database is ready!"

python manage.py migrate

python manage.py runserver 0.0.0.0:8000
