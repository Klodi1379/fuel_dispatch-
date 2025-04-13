from django.core.management.base import BaseCommand
from notifications.tasks import check_notifications

class Command(BaseCommand):
    help = 'Kontrollon dhe dërgon njoftime për nivele të ulëta karburanti dhe mirëmbajtje automjetesh'

    def handle(self, *args, **options):
        self.stdout.write('Duke kontrolluar për njoftime...')
        check_notifications()
        self.stdout.write(self.style.SUCCESS('Kontrolli i njoftimeve përfundoi me sukses!'))
