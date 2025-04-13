from rest_framework import serializers
from .models import VehicleLocation, Route, RouteWaypoint

class VehicleLocationSerializer(serializers.ModelSerializer):
    vehicle_license_plate = serializers.CharField(source='vehicle.license_plate', read_only=True)
    
    class Meta:
        model = VehicleLocation
        fields = ['id', 'vehicle', 'vehicle_license_plate', 'latitude', 'longitude', 
                  'altitude', 'speed', 'heading', 'timestamp']

class RouteWaypointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteWaypoint
        fields = ['id', 'order', 'latitude', 'longitude', 'name', 'stop_time']

class RouteSerializer(serializers.ModelSerializer):
    waypoints = RouteWaypointSerializer(many=True, read_only=True)
    dispatch_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Route
        fields = ['id', 'dispatch', 'dispatch_details', 'start_location', 'end_location',
                  'estimated_distance', 'estimated_duration', 'actual_duration',
                  'started_at', 'completed_at', 'status', 'route_data', 
                  'created_at', 'updated_at', 'waypoints']
    
    def get_dispatch_details(self, obj):
        return {
            'id': obj.dispatch.id,
            'vehicle': obj.dispatch.vehicle.license_plate,
            'driver': obj.dispatch.driver.username if obj.dispatch.driver else None,
            'dispatch_date': obj.dispatch.dispatch_date
        }
