#!/bin/sh

# Wait for database to be ready
python wait_for_db.py

# Apply database migrations
echo "Applying database migrations..."

# First, migrate the auth and contenttypes apps
python manage.py migrate auth
python manage.py migrate contenttypes

# Then migrate the rest of the apps
python manage.py migrate --fake-initial

# Collect static files (if needed)
if [ "$DJANGO_ENV" = "production" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Create superuser if needed
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput
fi

# Start server
if [ "$DJANGO_ENV" = "production" ]; then
    echo "Starting production server..."
    gunicorn --bind 0.0.0.0:8000 TRUCK_DISPACHER.wsgi:application
else
    echo "Starting development server..."
    python manage.py runserver 0.0.0.0:8000
fi
