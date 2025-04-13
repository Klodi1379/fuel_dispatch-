import requests
import json
from django.conf import settings

class RouteOptimizationService:
    """Shërbimi për optimizimin e rrugës duke përdorur API të OpenStreetMap (OSRM)"""
    
    def __init__(self):
        self.base_url = "https://router.project-osrm.org"
    
    def optimize_route(self, start_point, end_point, waypoints=None):
        """
        Optimizon një rrugë duke përdorur OSRM.
        
        Args:
            start_point: (latitude, longitude) e pikës fillestare
            end_point: (latitude, longitude) e pikës përfundimtare
            waypoints: lista opsionale e (latitude, longitude) për pikat e ndërmjetme
        
        Returns:
            Të dhënat e optimizuara të rrugës, ose None nëse ka dështuar
        """
        # Formato pikën e fillimit
        coordinates = f"{start_point[1]},{start_point[0]}"
        
        # Shto waypoints nëse ekzistojnë
        if waypoints:
            for point in waypoints:
                coordinates += f";{point[1]},{point[0]}"
        
        # Shto pikën e fundit
        coordinates += f";{end_point[1]},{end_point[0]}"
        
        # Ndërto URL-në e API
        url = f"{self.base_url}/route/v1/driving/{coordinates}?overview=full&alternatives=false&steps=true"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                route_data = response.json()
                return self._parse_route_data(route_data)
            else:
                print(f"Gabim në API: {response.status_code}")
                return None
        except Exception as e:
            print(f"Gabim gjatë kërkesës për optimizimin e rrugës: {e}")
            return None
    
    def _parse_route_data(self, route_data):
        """Përpunon të dhënat e rrugës nga OSRM"""
        if route_data['code'] != 'Ok':
            return None
        
        route = route_data['routes'][0]
        
        result = {
            'distance': route['distance'] / 1000,  # konverto në km
            'duration': route['duration'] / 60,    # konverto në minuta
            'geometry': route['geometry'],         # të dhënat GeoJSON të rrugës
            'waypoints': []
        }
        
        # Përpunon pikat e rrugës
        for waypoint in route_data['waypoints']:
            result['waypoints'].append({
                'location': [waypoint['location'][1], waypoint['location'][0]],  # lat, lng
                'name': waypoint.get('name', '')
            })
        
        return result
