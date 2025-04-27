from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import VehicleLocation, Route
from .serializers import VehicleLocationSerializer, RouteSerializer
from truck.models import Vehicle
import json
from decimal import Decimal

# Custom JSON encoder to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

@login_required
def tracking_dashboard(request):
    """Paraqet dashboardin e gjurmimit të automjeteve"""
    # Check if a specific vehicle ID is requested
    selected_vehicle_id = request.GET.get('vehicle_id')
    if selected_vehicle_id:
        try:
            selected_vehicle_id = int(selected_vehicle_id)
        except (ValueError, TypeError):
            selected_vehicle_id = None

    # Get active vehicles
    active_vehicles = Vehicle.objects.filter(is_active=True)

    # Get the latest location for each vehicle
    latest_locations = []
    for vehicle in active_vehicles:
        location = VehicleLocation.objects.filter(vehicle=vehicle).order_by('-timestamp').first()
        if location:
            latest_locations.append(location)

    # Serialize the locations for JavaScript
    serializer = VehicleLocationSerializer(latest_locations, many=True)
    import json

    # Create a dictionary for easy lookup in JavaScript
    vehicle_locations_dict = {}
    for location in serializer.data:
        vehicle_id = location['vehicle']
        vehicle_locations_dict[vehicle_id] = location

    context = {
        'vehicles': active_vehicles,
        'vehicle_locations': json.dumps(vehicle_locations_dict, cls=DecimalEncoder),
        'selected_vehicle_id': selected_vehicle_id,
        'page_title': 'Real-Time Vehicle Tracking'
    }
    return render(request, 'tracking/dashboard.html', context)

class VehicleLocationViewSet(viewsets.ModelViewSet):
    queryset = VehicleLocation.objects.all().order_by('-timestamp')
    serializer_class = VehicleLocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def latest(self, request):
        """Kthehet vendndodhja e fundit për çdo automjet"""
        vehicles = Vehicle.objects.filter(is_active=True)
        latest_locations = []

        for vehicle in vehicles:
            location = VehicleLocation.objects.filter(vehicle=vehicle).order_by('-timestamp').first()
            if location:
                latest_locations.append(location)

        serializer = self.get_serializer(latest_locations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def history(self, request, pk=None):
        """Kthehe historikun e vendndodhjeve të një automjeti"""
        try:
            vehicle = Vehicle.objects.get(pk=pk)
            # Merrni opsionalisht parametrat e filtrimit të datës
            from_date = request.query_params.get('from')
            to_date = request.query_params.get('to')

            locations = VehicleLocation.objects.filter(vehicle=vehicle)
            if from_date:
                locations = locations.filter(timestamp__gte=from_date)
            if to_date:
                locations = locations.filter(timestamp__lte=to_date)

            serializer = self.get_serializer(locations, many=True)
            return Response(serializer.data)
        except Vehicle.DoesNotExist:
            return Response(
                {"error": "Automjeti nuk u gjet"},
                status=status.HTTP_404_NOT_FOUND
            )

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['POST'])
    def optimize(self, request, pk=None):
        """Optimizon rrugën për një dispatch të dhënë"""
        from .route_service import RouteOptimizationService

        try:
            route = self.get_object()

            # Merrni pikën fillestare dhe përfundimtare
            start_point = (float(route.start_location.latitude), float(route.start_location.longitude))
            end_point = (float(route.end_location.latitude), float(route.end_location.longitude))

            # Merrni waypoints nga rruga
            waypoints = []
            for wp in route.waypoints.all().order_by('order'):
                waypoints.append((float(wp.latitude), float(wp.longitude)))

            # Optimizo rrugën
            router = RouteOptimizationService()
            optimized_route = router.optimize_route(start_point, end_point, waypoints)

            if optimized_route:
                # Përditëso rrugën me të dhënat e optimizuara
                route.estimated_distance = optimized_route['distance']
                route.estimated_duration = optimized_route['duration']
                route.route_data = optimized_route
                route.save()

                serializer = self.get_serializer(route)
                return Response(serializer.data)
            else:
                return Response(
                    {"error": "Nuk u arrit të optimizohej rruga"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"error": f"Gabim gjatë optimizimit të rrugës: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
