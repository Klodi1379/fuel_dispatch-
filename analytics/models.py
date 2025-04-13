from django.db import models
from django.contrib.auth.models import User
from fuelstation.models import FuelStation, FuelTank
from django.utils import timezone

class Report(models.Model):
    """Modeli për raporte të ruajtura"""

    REPORT_TYPES = [
        ('FUEL_CONSUMPTION', 'Konsumi i Karburantit'),
        ('DELIVERY_EFFICIENCY', 'Efiçenca e Dërgesave'),
        ('VEHICLE_USAGE', 'Përdorimi i Automjeteve'),
        ('STATION_INVENTORY', 'Inventari i Stacioneve'),
        ('CUSTOM', 'Raport i Personalizuar')
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    parameters = models.JSONField(null=True, blank=True, help_text="Parametrat e përdorur për gjenerimin e raportit")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    last_generated = models.DateTimeField(default=timezone.now)
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, null=True, blank=True,
                                        choices=[
                                            ('DAILY', 'Çdo ditë'),
                                            ('WEEKLY', 'Çdo javë'),
                                            ('MONTHLY', 'Çdo muaj')
                                        ])

    def __str__(self):
        return self.title

class ReportData(models.Model):
    """Të dhënat e gjeneruara nga raportet"""

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='data_sets')
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()
    chart_config = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Të dhënat për {self.report.title} - {self.generated_at}"

class FuelConsumptionStat(models.Model):
    """Statistika të konsumit të karburantit (për përdorim në analitikë)"""

    fuel_station = models.ForeignKey(FuelStation, on_delete=models.CASCADE, related_name='consumption_stats')
    fuel_type = models.CharField(max_length=20, choices=FuelTank.FUEL_TYPES)
    date = models.DateField()
    quantity_delivered = models.IntegerField(default=0, help_text="Sasia e dorëzuar në litra")
    quantity_sold = models.IntegerField(default=0, help_text="Sasia e shitur në litra")

    class Meta:
        unique_together = ['fuel_station', 'fuel_type', 'date']

    def __str__(self):
        return f"{self.fuel_station} - {self.get_fuel_type_display()} - {self.date}"

class DeliveryPerformanceStat(models.Model):
    """Statistika të performancës së dorëzimit"""

    date = models.DateField()
    total_dispatches = models.IntegerField(default=0)
    completed_on_time = models.IntegerField(default=0)
    delayed_deliveries = models.IntegerField(default=0)
    cancelled_deliveries = models.IntegerField(default=0)
    average_dispatch_time = models.IntegerField(help_text="Koha mesatare në minuta")

    class Meta:
        unique_together = ['date']

    def __str__(self):
        return f"Performanca e dorëzimit për {self.date}"
