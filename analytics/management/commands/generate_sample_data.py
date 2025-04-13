from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from fuelstation.models import FuelStation, FuelTank
from analytics.models import FuelConsumptionStat, DeliveryPerformanceStat

class Command(BaseCommand):
    help = 'Gjeneron të dhëna shembull për analitikën'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Numri i ditëve për të cilat do të gjenerohen të dhëna')

    def handle(self, *args, **options):
        days = options['days']
        today = timezone.now().date()
        
        self.stdout.write('Duke gjeneruar të dhëna shembull për analitikën...')
        
        # Gjenero të dhëna për konsumin e karburantit
        self.generate_fuel_consumption_data(days, today)
        
        # Gjenero të dhëna për efiçencën e dërgesave
        self.generate_delivery_performance_data(days, today)
        
        self.stdout.write(self.style.SUCCESS(f'Të dhënat u gjeneruan me sukses për {days} ditë!'))
    
    def generate_fuel_consumption_data(self, days, today):
        """Gjeneron të dhëna për konsumin e karburantit"""
        stations = FuelStation.objects.all()
        
        if not stations.exists():
            self.stdout.write(self.style.WARNING('Nuk u gjetën stacione karburanti. Ju lutemi krijoni stacione para se të gjeneroni të dhëna.'))
            return
        
        # Fshi të dhënat ekzistuese
        FuelConsumptionStat.objects.all().delete()
        
        for station in stations:
            # Merr llojet e karburantit për këtë stacion
            fuel_tanks = FuelTank.objects.filter(fuel_station=station)
            fuel_types = [tank.fuel_type for tank in fuel_tanks]
            
            if not fuel_types:
                continue
            
            for day in range(days):
                date = today - timedelta(days=day)
                
                for fuel_type in fuel_types:
                    # Gjenero të dhëna të rastësishme por realiste
                    base_quantity = random.randint(500, 2000)  # Sasia bazë në litra
                    
                    # Dërgesat ndodhin më rrallë
                    if random.random() < 0.3:  # 30% shans për dërgesë
                        quantity_delivered = base_quantity * random.uniform(1.5, 3)
                    else:
                        quantity_delivered = 0
                    
                    # Shitjet ndodhin çdo ditë
                    quantity_sold = base_quantity * random.uniform(0.7, 1.3)
                    
                    # Krijo statistikën
                    FuelConsumptionStat.objects.create(
                        fuel_station=station,
                        fuel_type=fuel_type,
                        date=date,
                        quantity_delivered=int(quantity_delivered),
                        quantity_sold=int(quantity_sold)
                    )
        
        self.stdout.write(f'U gjeneruan {FuelConsumptionStat.objects.count()} të dhëna për konsumin e karburantit')
    
    def generate_delivery_performance_data(self, days, today):
        """Gjeneron të dhëna për efiçencën e dërgesave"""
        # Fshi të dhënat ekzistuese
        DeliveryPerformanceStat.objects.all().delete()
        
        for day in range(days):
            date = today - timedelta(days=day)
            
            # Gjenero të dhëna të rastësishme por realiste
            total_dispatches = random.randint(5, 20)
            
            # Llogarit numrin e dërgesave në kohë, të vonuara dhe të anuluara
            completed_on_time = int(total_dispatches * random.uniform(0.6, 0.9))
            delayed_deliveries = int(total_dispatches * random.uniform(0.05, 0.3))
            cancelled_deliveries = total_dispatches - completed_on_time - delayed_deliveries
            
            # Sigurohu që numrat janë të vlefshëm
            if cancelled_deliveries < 0:
                cancelled_deliveries = 0
            
            # Koha mesatare e dërgesës (në minuta)
            average_dispatch_time = random.randint(30, 120)
            
            # Krijo statistikën
            DeliveryPerformanceStat.objects.create(
                date=date,
                total_dispatches=total_dispatches,
                completed_on_time=completed_on_time,
                delayed_deliveries=delayed_deliveries,
                cancelled_deliveries=cancelled_deliveries,
                average_dispatch_time=average_dispatch_time
            )
        
        self.stdout.write(f'U gjeneruan {DeliveryPerformanceStat.objects.count()} të dhëna për efiçencën e dërgesave')
