from django.db import models

class Vehicle(models.Model):
    license_plate = models.CharField(max_length=20, unique=True, help_text="License plate number")
    chassis_number = models.CharField(max_length=50, unique=True, help_text="Chassis number")
    compartment_number = models.IntegerField(help_text="Number of compartments")
    separated_cab = models.BooleanField(default=False, help_text="Whether the cab is separated from the tank")
    has_pump = models.BooleanField(default=False, help_text="Whether it has a pump")
    hose_length = models.IntegerField(blank=True, null=True, help_text="Hose length in meters, if any")
    free_flow_unloading = models.BooleanField(default=False, help_text="Whether it unloads by free flow")

    def __str__(self):
        return f"{self.license_plate} - {self.chassis_number}"

class Compartment(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='compartments')
    capacity = models.IntegerField(help_text="Capacity in liters of the compartment")

    def __str__(self):
        return f"{self.vehicle.license_plate} Compartment - {self.capacity} liters"
