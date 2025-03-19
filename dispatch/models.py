from django.db import models
from django.contrib.auth.models import User
from truck.models import Vehicle, Compartment
from fuelstation.models import FuelStation

class Dispatch(models.Model):
    STATUS_CHOICES = [
        ('PLANNED', 'Planifikuar'),
        ('IN_PROGRESS', 'Në Proces'),
        ('COMPLETED', 'Përfunduar'),
        ('CANCELLED', 'Anuluar')
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='dispatches')
    fuel_station = models.ForeignKey(FuelStation, on_delete=models.CASCADE, related_name='dispatches')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_dispatches')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_dispatches')
    dispatch_date = models.DateTimeField()
    arrival_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dispatch #{self.id} - {self.vehicle} to {self.fuel_station}"

class Load(models.Model):
    dispatch = models.ForeignKey(Dispatch, on_delete=models.CASCADE, related_name='loads')
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)
    fuel_type = models.CharField(max_length=50)
    quantity = models.IntegerField(help_text="Sasia në litra")
    loaded = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"Load for {self.dispatch} - {self.fuel_type} ({self.quantity}L)"
