#!/usr/bin/env python
"""
Script to test the vehicle location API
"""
import os
import django
import requests
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TRUCK_DISPACHER.settings')
django.setup()

def test_api():
    """Test the vehicle location API"""
    print("Testing vehicle location API...")
    
    # Get a session with authentication
    from django.contrib.auth.models import User
    from django.test import Client
    
    # Create a test client
    client = Client()
    
    # Try to get a user for login
    try:
        user = User.objects.first()
        if user:
            # Login with the first user
            client.login(username=user.username, password='password')  # Assuming password is 'password'
            print(f"Logged in as {user.username}")
        else:
            print("No users found in the database. Creating a test user...")
            # Create a test user
            user = User.objects.create_user(username='testuser', password='testpassword')
            client.login(username='testuser', password='testpassword')
            print(f"Created and logged in as testuser")
    except Exception as e:
        print(f"Error logging in: {e}")
        return
    
    # Test the API endpoint
    response = client.get('/tracking/api/locations/latest/')
    
    # Check the response
    if response.status_code == 200:
        print("API endpoint returned status 200 OK")
        
        # Parse the response
        data = json.loads(response.content)
        
        # Check if we have data
        if data:
            print(f"API returned {len(data)} location records:")
            for location in data:
                print(f"- Vehicle ID: {location['vehicle']}, License: {location['vehicle_license_plate']}")
                print(f"  Lat: {location['latitude']}, Lng: {location['longitude']}, Speed: {location['speed']}")
                print(f"  Timestamp: {location['timestamp']}")
        else:
            print("API returned an empty list. No location data found.")
    else:
        print(f"API endpoint returned status {response.status_code}")
        print(response.content)

if __name__ == '__main__':
    test_api()
