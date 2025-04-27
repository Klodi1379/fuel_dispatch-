#!/usr/bin/env python
"""
Script to check vehicle and location data in the database
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TRUCK_DISPACHER.settings')
django.setup()

# Import models
from truck.models import Vehicle
from tracking.models import VehicleLocation

def check_data():
    """Check vehicle and location data in the database"""
    print("Checking vehicle data...")
    
    # Check vehicles
    vehicles = Vehicle.objects.filter(is_active=True)
    print(f"Found {vehicles.count()} active vehicles:")
    for vehicle in vehicles:
        print(f"- {vehicle.license_plate} (ID: {vehicle.id})")
    
    print("\nChecking location data...")
    
    # Check locations
    for vehicle in vehicles:
        locations = VehicleLocation.objects.filter(vehicle=vehicle).order_by('-timestamp')
        if locations.exists():
            latest = locations.first()
            print(f"Vehicle {vehicle.license_plate} has {locations.count()} location records.")
            print(f"  Latest: Lat {latest.latitude}, Lng {latest.longitude}, Speed: {latest.speed}, Time: {latest.timestamp}")
        else:
            print(f"Vehicle {vehicle.license_plate} has NO location records.")
    
    # Check total location records
    total_locations = VehicleLocation.objects.count()
    print(f"\nTotal location records in database: {total_locations}")

if __name__ == '__main__':
    check_data()
