from django.db import models
from django.contrib.auth.models import User
from truck.models import Vehicle
from fuelstation.models import FuelStation
from django.utils import timezone

class VehicleLocation(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    speed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Shpejtësia në km/h")
    heading = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Drejtimi në gradë")
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.vehicle} në {self.timestamp}"

class Route(models.Model):
    STATUS_CHOICES = [
        ('PLANNED', 'Planifikuar'),
        ('IN_PROGRESS', 'Në Progres'),
        ('COMPLETED', 'Përfunduar'),
        ('CANCELLED', 'Anuluar')
    ]

    dispatch = models.OneToOneField('dispatch.Dispatch', on_delete=models.CASCADE, related_name='route')
    start_location = models.ForeignKey(FuelStation, on_delete=models.SET_NULL, null=True, related_name='routes_as_start')
    end_location = models.ForeignKey(FuelStation, on_delete=models.SET_NULL, null=True, related_name='routes_as_end')
    estimated_distance = models.DecimalField(max_digits=10, decimal_places=2, help_text="Distanca në kilometra")
    estimated_duration = models.IntegerField(help_text="Kohëzgjatja e parashikuar në minuta")
    actual_duration = models.IntegerField(null=True, blank=True, help_text="Kohëzgjatja faktike në minuta")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    route_data = models.JSONField(null=True, blank=True, help_text="Të dhënat e rrugës nga API")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rruga për {self.dispatch} - {self.status}"

class RouteWaypoint(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='waypoints')
    order = models.IntegerField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    name = models.CharField(max_length=255, null=True, blank=True)
    stop_time = models.IntegerField(default=0, help_text="Koha e ndalimit në minuta")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Pikë në rrugën {self.route_id} (Urdhër: {self.order})"
