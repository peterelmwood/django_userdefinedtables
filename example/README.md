# django_userdefinedtables Example Application

This example demonstrates how to use the `django_userdefinedtables` package in a Django application. It includes a working implementation with a user interface for creating and managing user-defined tables.

## What's Included

- **User Playground**: Interactive interface for creating Lists (tables), Columns, and Rows
- **Django Admin**: Pre-configured admin interface for all models
- **Sample Data**: Bootstrap templates and forms for a complete user experience

## Running the Example

### With Docker Compose (Recommended)

The easiest way to run the example is using Docker Compose, which sets up both the web application and PostgreSQL database:

```bash
cd example
docker compose up
```

After the containers are running, navigate to http://localhost:8001 in your browser.

To stop the application, press `Ctrl+C` or run:
```bash
docker compose down
```

### With Docker (Manual Build)

If you prefer to use Docker without Compose, you'll need to set up a PostgreSQL database separately and provide the connection details via environment variables:

```bash
cd example
docker build -t django_userdefinedtables .
docker run --publish 8001:8000 \
  --env POSTGRES_NAME=your_db_name \
  --env POSTGRES_USER=your_db_user \
  --env POSTGRES_PASSWORD=your_db_password \
  --env POSTGRES_HOST=your_db_host \
  django_userdefinedtables
```

### Without Docker

1. Ensure PostgreSQL is running and accessible
2. Set required environment variables:
   ```bash
   export POSTGRES_NAME=your_db_name
   export POSTGRES_USER=your_db_user
   export POSTGRES_PASSWORD=your_db_password
   export POSTGRES_HOST=db  # or your database host
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver 8001
   ```

## Exploring the Example

Once running, you can:
- Visit the homepage at http://localhost:8001
- Access the playground at http://localhost:8001/playground/
- Login to admin at http://localhost:8001/admin/ (if you created a superuser)

## Features Demonstrated

- Creating user-defined Lists (tables)
- Adding different types of Columns (text, numbers, dates, etc.)
- Managing Rows and Entries
- Form validation and error handling
- Integration with Django's admin interface
