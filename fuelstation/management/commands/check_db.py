from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check database structure'

    def handle(self, *args, **kwargs):
        self.stdout.write('Checking database structure...')
        
        # Check FuelTank table structure
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(fuelstation_fueltank)")
            columns = cursor.fetchall()
            
            self.stdout.write('FuelTank table columns:')
            for column in columns:
                self.stdout.write(f'  {column}')
