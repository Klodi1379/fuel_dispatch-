# Monkey patch Django's migration system to skip migration checks
from django.core.management.commands import runserver

# Store the original check_migrations method
original_check_migrations = runserver.Command.check_migrations

# Replace it with a no-op function
def no_op_check_migrations(self):
    self.stdout.write("Migration checks disabled.")

# Apply the monkey patch
runserver.Command.check_migrations = no_op_check_migrations
