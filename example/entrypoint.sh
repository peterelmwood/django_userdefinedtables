#!/bin/bash

# Validate required environment variables using parameter expansion
: "${POSTGRES_NAME:?Error: POSTGRES_NAME environment variable is required}"
: "${POSTGRES_USER:?Error: POSTGRES_USER environment variable is required}"
: "${POSTGRES_PASSWORD:?Error: POSTGRES_PASSWORD environment variable is required}"

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
    sys.exit(2)
END
do
  EXIT_CODE=$?
  if [ $EXIT_CODE -eq 1 ]; then
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
      echo "Database did not become ready after $MAX_RETRIES seconds. Exiting."
      exit 1
    fi
    echo "Database not ready yet, retrying... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 1
  else
    # For any non-transient error, exit immediately with the same code
    exit $EXIT_CODE
  fi
done

echo "Database is ready!"

python3 manage.py migrate

python3 manage.py runserver 0.0.0.0:8000
