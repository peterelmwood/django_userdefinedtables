# django_userdefinedtables Example
This section of code may be pulled down separately from the rest of the codebase, or along with it.
After it is pulled down locally, it can be run with or without Docker:

## With Docker Compose (Recommended)
The easiest way to run the example is using Docker Compose, which sets up both the web application and PostgreSQL database:

```bash
docker compose up
```

After the build is complete and the app is running, navigate to http://localhost:8001 in a browser window.

To stop the application, press `Ctrl+C` or run:
```bash
docker compose down
```

## With Docker (Standalone)
If you prefer to use Docker without Compose, you'll need to set up a PostgreSQL database separately and provide the connection details via environment variables:

```bash
docker build -t django_userdefinedtables .
docker run -p 8001:8000 \
  -e POSTGRES_NAME=your_db_name \
  -e POSTGRES_USER=your_db_user \
  -e POSTGRES_PASSWORD=your_db_password \
  -e POSTGRES_HOST=your_db_host \
  django_userdefinedtables
```

Note: You'll also need to update `settings.py` to use the `POSTGRES_HOST` environment variable instead of the hardcoded "db" hostname.

## Without Docker
To run locally without Docker:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up a PostgreSQL database and update the `DATABASES` configuration in `settings.py` to point to your database.

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

5. Navigate to http://localhost:8000 in a browser window.
