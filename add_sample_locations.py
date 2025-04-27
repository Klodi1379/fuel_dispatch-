#!/usr/bin/env python
"""
Script to add sample location data for vehicles
"""
import os
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TRUCK_DISPACHER.settings')
django.setup()

# Import models
from django.utils import timezone
from truck.models import Vehicle
from tracking.models import VehicleLocation

def add_sample_locations():
    """Add sample location data for vehicles"""
    print("Adding sample location data...")
    
    # Albania coordinates (approximate center and bounds)
    albania_center = (41.3275, 19.8187)  # Tirana
    
    # Major cities in Albania with their coordinates
    cities = [
        {"name": "Tirana", "lat": 41.3275, "lng": 19.8187},
        {"name": "Durres", "lat": 41.3233, "lng": 19.4542},
        {"name": "Vlore", "lat": 40.4667, "lng": 19.4833},
        {"name": "Shkoder", "lat": 42.0692, "lng": 19.5033},
        {"name": "Fier", "lat": 40.7239, "lng": 19.5556},
        {"name": "Elbasan", "lat": 41.1167, "lng": 20.0833},
        {"name": "Korce", "lat": 40.6167, "lng": 20.7667},
        {"name": "Berat", "lat": 40.7058, "lng": 19.9522},
        {"name": "Lushnje", "lat": 40.9419, "lng": 19.7056},
        {"name": "Pogradec", "lat": 40.9025, "lng": 20.6525}
    ]
    
    # Get all active vehicles
    vehicles = Vehicle.objects.filter(is_active=True)
    
    if not vehicles.exists():
        print("No active vehicles found in the database.")
        return
    
    # Delete existing location records (optional)
    VehicleLocation.objects.all().delete()
    print(f"Deleted all existing location records.")
    
    # Create location records for each vehicle
    for vehicle in vehicles:
        # Assign a random city to this vehicle
        city = random.choice(cities)
        
        # Create a location record with the city's coordinates
        # Add small random offsets to make vehicles appear in different places within the city
        lat_offset = Decimal(str(random.uniform(-0.01, 0.01)))
        lng_offset = Decimal(str(random.uniform(-0.01, 0.01)))
        
        latitude = Decimal(str(city["lat"])) + lat_offset
        longitude = Decimal(str(city["lng"])) + lng_offset
        
        # Random speed between 0 and 90 km/h
        speed = Decimal(str(random.randint(0, 90)))
        
        # Create the location record
        location = VehicleLocation.objects.create(
            vehicle=vehicle,
            latitude=latitude,
            longitude=longitude,
            speed=speed,
            heading=Decimal(str(random.randint(0, 359))),
            timestamp=timezone.now() - timedelta(minutes=random.randint(0, 60))
        )
        
        print(f"Created location for {vehicle.license_plate} in {city['name']}: Lat {latitude}, Lng {longitude}, Speed {speed} km/h")
    
    # Count total location records
    total_locations = VehicleLocation.objects.count()
    print(f"\nTotal location records created: {total_locations}")

if __name__ == '__main__':
    add_sample_locations()
