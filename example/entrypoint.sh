#!/bin/bash

# Validate required environment variables
if [ -z "$POSTGRES_NAME" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    echo "Error: Required environment variables are not set."
    echo "Please set POSTGRES_NAME, POSTGRES_USER, and POSTGRES_PASSWORD."
    exit 1
fi

# Wait for database to be ready
echo "Waiting for database..."
MAX_RETRIES=30
RETRY_COUNT=0

# Use a small Python script to check database connection without exposing credentials in process list
until python3 << 'END'
import psycopg2
import os
import sys

try:
    conn = psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'db'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        dbname=os.environ.get('POSTGRES_NAME')
    )
    conn.close()
    sys.exit(0)
except psycopg2.OperationalError as e:
    # Expected error when database is not ready yet
    sys.exit(1)
except Exception as e:
    # Unexpected error - log it
    print(f"Unexpected error connecting to database: {e}", file=sys.stderr)
    sys.exit(1)
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
