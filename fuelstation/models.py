from django.db import models
from django.urls import reverse

class FuelStation(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('fuelstation:fuelstation_detail', kwargs={'pk': self.pk})

class FuelTank(models.Model):
    FUEL_TYPES = [
        ('DIESEL', 'Diesel'),
        ('GASOLINE_95', 'Gasoline 95'),
        ('GASOLINE_98', 'Gasoline 98'),
    ]

    fuel_station = models.ForeignKey(FuelStation, on_delete=models.CASCADE, related_name='fuel_tanks')
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES)
    capacity = models.IntegerField(help_text="Capacity in liters")
    current_level = models.IntegerField(help_text="Current fuel level in liters")

    def __str__(self):
        return f"{self.fuel_station.name} - {self.get_fuel_type_display()}"
