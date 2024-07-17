from django.db import models

class FuelStation(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class FuelTank(models.Model):
    station = models.ForeignKey(FuelStation, on_delete=models.CASCADE, related_name='fuel_tanks')
    fuel_type = models.CharField(max_length=50)  # e.g., 'Diesel', 'Unleaded', etc.
    capacity = models.IntegerField()

    def __str__(self):
        return f"{self.station.name} - {self.fuel_type} Tank ({self.capacity} liters)"