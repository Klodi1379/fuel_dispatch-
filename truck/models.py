from django.db import models

class Vehicle(models.Model):
    TYPE_CHOICES = [
        ('TANKER', 'Autobote'),
        ('TRUCK', 'Kamion'),
        ('TRAILER', 'Rimorkio')
    ]
    
    license_plate = models.CharField(max_length=20, unique=True, help_text="Numri i targës")
    chassis_number = models.CharField(max_length=50, unique=True, help_text="Numri i shasisë")
    vehicle_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='TANKER', help_text="Tipi i mjetit")
    compartment_number = models.IntegerField(help_text="Numri i dhomave")
    separated_cab = models.BooleanField(default=False, help_text="Nëse kabina është e ndarë nga cisterna")
    has_pump = models.BooleanField(default=False, help_text="Nëse ka pompë")
    hose_length = models.IntegerField(blank=True, null=True, help_text="Gjatësia e tubit në metra, nëse ka")
    free_flow_unloading = models.BooleanField(default=False, help_text="Nëse shkarkon me rrjedhje të lirë")
    year_of_manufacture = models.IntegerField(blank=True, null=True, help_text="Viti i prodhimit")
    last_maintenance_date = models.DateField(blank=True, null=True, help_text="Data e mirëmbajtjes së fundit")
    next_maintenance_date = models.DateField(blank=True, null=True, help_text="Data e mirëmbajtjes së ardhshme të planifikuar")
    is_active = models.BooleanField(default=True, help_text="Nëse mjeti është aktualisht aktiv")
    notes = models.TextField(blank=True, null=True, help_text="Shënime shtesë për mjetin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_capacity(self):
        return sum(compartment.capacity for compartment in self.compartments.all())
    
    @property
    def capacity(self):
        return self.total_capacity

    def __str__(self):
        return f"{self.license_plate} - {self.chassis_number}"

class Compartment(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='compartments')
    capacity = models.IntegerField(help_text="Kapaciteti në litra i dhomës")
    compartment_number = models.IntegerField(default=1, help_text="Numri rendor i dhomës")
    is_active = models.BooleanField(default=True, help_text="Nëse dhoma është aktualisht aktive")
    
    class Meta:
        ordering = ['compartment_number']

    def __str__(self):
        return f"{self.vehicle.license_plate} Dhoma {self.compartment_number} - {self.capacity} litra"
