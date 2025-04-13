#!/bin/bash

set -e

# Create static directory if it doesn't exist
mkdir -p /app/static

# Create a temporary file to disable migration checks
cat > /app/TRUCK_DISPACHER/disable_migration_check.py << 'EOF'
# Monkey patch Django's migration system to skip migration checks
from django.core.management.commands import runserver

# Store the original check_migrations method
original_check_migrations = runserver.Command.check_migrations

# Replace it with a no-op function
def no_op_check_migrations(self):
    self.stdout.write("Migration checks disabled.")

# Apply the monkey patch
runserver.Command.check_migrations = no_op_check_migrations
EOF

# Set the PYTHONPATH to include the current directory
export PYTHONPATH=$PYTHONPATH:/app

# Start the Django development server with the monkey patch
echo "Starting Django server..."
echo "NOTE: Migrations are skipped. Please run migrations manually before starting the container."
exec python -c "import TRUCK_DISPACHER.disable_migration_check; from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000', '--noreload'])"
