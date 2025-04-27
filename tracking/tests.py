from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from truck.models import Vehicle
from .models import VehicleLocation
from decimal import Decimal
import json
from django.utils import timezone

class VehicleMarkerPositionTest(TestCase):
    """Test case for verifying vehicle marker positions on the map"""

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Create test vehicles
        self.vehicle1 = Vehicle.objects.create(
            license_plate='TEST001',
            chassis_number='CHASSIS001',
            vehicle_type='TANKER',
            compartment_number=2,
            is_active=True
        )

        self.vehicle2 = Vehicle.objects.create(
            license_plate='TEST002',
            chassis_number='CHASSIS002',
            vehicle_type='TRUCK',
            compartment_number=1,
            is_active=True
        )

        # Create test locations
        self.location1 = VehicleLocation.objects.create(
            vehicle=self.vehicle1,
            latitude=Decimal('41.3275'),
            longitude=Decimal('19.8187'),
            speed=Decimal('65.5'),
            timestamp=timezone.now()
        )

        self.location2 = VehicleLocation.objects.create(
            vehicle=self.vehicle2,
            latitude=Decimal('41.3233'),
            longitude=Decimal('19.4542'),
            speed=Decimal('0.0'),
            timestamp=timezone.now()
        )

        # Create a test client
        self.client = Client()

        # Login the test user
        self.client.login(username='testuser', password='testpassword')

    def test_dashboard_loads_with_vehicles(self):
        """Test that the dashboard loads with the correct vehicles"""
        response = self.client.get(reverse('tracking:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST001')
        self.assertContains(response, 'TEST002')

    def test_api_returns_correct_coordinates(self):
        """Test that the API returns the correct coordinates for vehicles"""
        response = self.client.get('/tracking/api/locations/latest/')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(len(data), 2)

        # Check that the coordinates are correct
        coordinates = {item['vehicle']: (item['latitude'], item['longitude']) for item in data}

        self.assertEqual(Decimal(coordinates[self.vehicle1.id][0]), self.location1.latitude)
        self.assertEqual(Decimal(coordinates[self.vehicle1.id][1]), self.location1.longitude)
        self.assertEqual(Decimal(coordinates[self.vehicle2.id][0]), self.location2.latitude)
        self.assertEqual(Decimal(coordinates[self.vehicle2.id][1]), self.location2.longitude)

    def test_marker_position_calculation(self):
        """Test the JavaScript function that calculates marker positions"""
        # This is a JavaScript test that we'll run using Selenium or similar
        # For now, we'll just check that the dashboard template contains the correct code
        response = self.client.get(reverse('tracking:dashboard'))

        # Check that the template contains the code to parse coordinates
        self.assertContains(response, 'const lat = parseFloat(vehicle.latitude);')
        self.assertContains(response, 'const lng = parseFloat(vehicle.longitude);')

        # Check that the template contains the code to create markers with the parsed coordinates
        self.assertContains(response, 'L.marker([lat, lng],')

        # Check that the icon anchor is set correctly
        self.assertContains(response, 'iconAnchor: [20, 40]')
