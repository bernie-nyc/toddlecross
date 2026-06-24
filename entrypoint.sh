#!/bin/sh

# We tell the script to stop running immediately if any command fails.
set -e

# We print a startup message to the logs.
echo "Starting Toddlecross entrypoint script..."

# We run database migrations to make sure our database tables are up to date.
echo "Running database migrations..."
python manage.py migrate --noinput

# We collect all static assets (like CSS files) into a single folder for WhiteNoise to serve.
echo "Collecting static files..."
python manage.py collectstatic --noinput

# We run our custom command to make sure the default admin account is created.
echo "Ensuring default superuser exists..."
python manage.py ensure_superuser

# We start Gunicorn, our production web server, binding it to port 8080.
# The exec command replaces this script process with Gunicorn.
echo "Starting Gunicorn application server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8080 --workers 3
