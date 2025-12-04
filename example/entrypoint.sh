#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
MAX_RETRIES=30
RETRY_COUNT=0

until python -c "import psycopg2; psycopg2.connect(host='${POSTGRES_HOST:-db}', user='$POSTGRES_USER', password='$POSTGRES_PASSWORD', dbname='$POSTGRES_NAME')" 2>/dev/null; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "Database did not become ready in time. Exiting."
    exit 1
  fi
  echo "Database not ready yet, retrying... ($RETRY_COUNT/$MAX_RETRIES)"
  sleep 1
done

echo "Database is ready!"

python manage.py migrate

python manage.py runserver 0.0.0.0:8000
