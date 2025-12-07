#!/usr/bin/env python3
"""
Entrypoint script for the Django application container.
Validates environment variables, waits for database readiness, and starts the application.
"""
import os
import sys
import time
import psycopg2
from psycopg2 import OperationalError


def validate_environment_variables():
    """Validate that required environment variables are set."""
    required_vars = ['POSTGRES_NAME', 'POSTGRES_USER', 'POSTGRES_PASSWORD']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Error: Required environment variables are not set: {', '.join(missing_vars)}", file=sys.stderr)
        sys.exit(1)


def wait_for_database(max_retries=30):
    """
    Wait for the database to become ready.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 30 seconds)
    
    Returns:
        True if database is ready, exits with error code otherwise
    """
    print("Waiting for database...")
    retry_count = 0
    
    db_config = {
        'host': os.environ.get('POSTGRES_HOST', 'db'),
        'user': os.environ.get('POSTGRES_USER'),
        'password': os.environ.get('POSTGRES_PASSWORD'),
        'dbname': os.environ.get('POSTGRES_NAME')
    }
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(**db_config)
            conn.close()
            print("Database is ready!")
            return True
        except OperationalError:
            # Expected error when database is not ready yet
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Database did not become ready after {max_retries} seconds. Exiting.", file=sys.stderr)
                sys.exit(1)
            print(f"Database not ready yet, retrying... ({retry_count}/{max_retries})")
            time.sleep(1)
        except Exception as e:
            # Unexpected error - configuration issue
            print(f"Unexpected error connecting to database: {e}", file=sys.stderr)
            sys.exit(2)


def run_migrations():
    """Run Django database migrations."""
    import subprocess
    print("Running migrations...")
    result = subprocess.run(['python3', 'manage.py', 'migrate'], check=False)
    if result.returncode != 0:
        print("Failed to run migrations", file=sys.stderr)
        sys.exit(1)


def start_server():
    """Start the Django development server."""
    import subprocess
    print("Starting Django development server...")
    # Use exec to replace the Python process with the server process
    os.execvp('python3', ['python3', 'manage.py', 'runserver', '0.0.0.0:8000'])


if __name__ == '__main__':
    validate_environment_variables()
    wait_for_database()
    run_migrations()
    start_server()
