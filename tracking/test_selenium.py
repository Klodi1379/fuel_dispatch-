from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from truck.models import Vehicle
from .models import VehicleLocation
from decimal import Decimal
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json

class MarkerPositionSeleniumTest(LiveServerTestCase):
    """Test case for verifying vehicle marker positions on the map using Selenium"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up Chrome options for headless testing
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Create a Chrome webdriver
        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
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
        
        # Create test locations with specific coordinates
        self.location1 = VehicleLocation.objects.create(
            vehicle=self.vehicle1,
            latitude=Decimal('41.3275'),
            longitude=Decimal('19.8187'),
            speed=Decimal('65.5'),
            timestamp=timezone.now()
        )
    
    def test_marker_position_on_map(self):
        """Test that markers are positioned correctly on the map"""
        # Login
        self.selenium.get(f'{self.live_server_url}/login/')
        username_input = self.selenium.find_element(By.NAME, 'username')
        password_input = self.selenium.find_element(By.NAME, 'password')
        username_input.send_keys('testuser')
        password_input.send_keys('testpassword')
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Navigate to tracking dashboard
        self.selenium.get(f'{self.live_server_url}/tracking/')
        
        # Wait for the map to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'vehicle-map'))
        )
        
        # Give time for markers to be added to the map
        time.sleep(2)
        
        # Execute JavaScript to get marker positions
        marker_positions = self.selenium.execute_script("""
            // Get all markers on the map
            const markers = Object.values(window.markers || {});
            if (markers.length === 0) return [];
            
            // Return the positions of all markers
            return markers.map(marker => {
                const latLng = marker.getLatLng();
                return {
                    id: marker.options.title || 'unknown',
                    lat: latLng.lat,
                    lng: latLng.lng
                };
            });
        """)
        
        # Check if we have markers
        self.assertTrue(len(marker_positions) > 0, "No markers found on the map")
        
        # Find our test vehicle marker
        test_marker = None
        for marker in marker_positions:
            if marker.get('id') == 'TEST001':
                test_marker = marker
                break
        
        # Verify the marker exists and has the correct position
        self.assertIsNotNone(test_marker, "Test vehicle marker not found")
        self.assertAlmostEqual(float(test_marker['lat']), float(self.location1.latitude), places=4)
        self.assertAlmostEqual(float(test_marker['lng']), float(self.location1.longitude), places=4)
        
        # Test that the marker is visible in the viewport
        is_visible = self.selenium.execute_script("""
            const map = window.map;
            const marker = Object.values(window.markers || {}).find(m => m.options.title === 'TEST001');
            if (!map || !marker) return false;
            
            return map.getBounds().contains(marker.getLatLng());
        """)
        
        self.assertTrue(is_visible, "Marker is not visible in the map viewport")
