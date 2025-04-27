from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
import json
from datetime import timedelta
from decimal import Decimal
from truck.models import Vehicle
from fuelstation.models import FuelStation, FuelTank
from dispatch.models import Dispatch
from tracking.models import VehicleLocation
from notifications.models import Notification

# Custom JSON encoder to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

@login_required
def dashboard(request):
    # Get current date and time
    now = timezone.now()
    today = now.date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # Get dispatch statistics
    try:
        # Use raw SQL to avoid created_at field issues
        from django.db import connection
        with connection.cursor() as cursor:
            # Count dispatches by status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM dispatch_dispatch
                GROUP BY status
            """)
            status_counts = dict(cursor.fetchall())

            # Get today's dispatches
            cursor.execute("""
                SELECT d.id, d.dispatch_date, d.status, v.license_plate, fs.name as station_name
                FROM dispatch_dispatch d
                LEFT JOIN truck_vehicle v ON d.vehicle_id = v.id
                LEFT JOIN fuelstation_fuelstation fs ON d.fuel_station_id = fs.id
                WHERE date(d.dispatch_date) = ?
                ORDER BY d.dispatch_date DESC
            """, [today.strftime('%Y-%m-%d')])
            columns = [col[0] for col in cursor.description]
            today_dispatches = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Get dispatch counts by day for the last 30 days
            cursor.execute("""
                SELECT date(dispatch_date) as date, COUNT(*) as count
                FROM dispatch_dispatch
                WHERE dispatch_date >= ?
                GROUP BY date(dispatch_date)
                ORDER BY date
            """, [(today - timedelta(days=30)).strftime('%Y-%m-%d')])
            dispatch_trend = {row[0]: row[1] for row in cursor.fetchall()}
    except Exception as e:
        print(f"Error fetching dispatch data: {e}")
        status_counts = {}
        today_dispatches = []
        dispatch_trend = {}

    # Get vehicle statistics
    total_vehicles = Vehicle.objects.count()
    active_vehicles = Vehicle.objects.filter(is_active=True).count()
    maintenance_vehicles = Vehicle.objects.filter(next_maintenance_date__lte=now).count()

    # Get recent vehicle locations
    try:
        # Get distinct vehicle IDs first
        vehicle_ids = VehicleLocation.objects.filter(
            timestamp__gte=now - timedelta(hours=24)
        ).values_list('vehicle_id', flat=True).distinct()

        # Then get the most recent location for each vehicle
        recent_locations = []
        for vid in vehicle_ids[:10]:
            loc = VehicleLocation.objects.filter(vehicle_id=vid).order_by('-timestamp').first()
            if loc:
                recent_locations.append(loc)
    except Exception as e:
        print(f"Error fetching vehicle locations: {e}")
        recent_locations = []

    # Get fuel station statistics
    try:
        total_stations = FuelStation.objects.count()

        # Get fuel levels
        fuel_levels = {}
        for fuel_type, _ in FuelTank.FUEL_TYPES:
            try:
                # Use raw SQL to avoid created_at field issues
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT SUM(current_level), SUM(capacity)
                        FROM fuelstation_fueltank
                        WHERE fuel_type = ?
                    """, [fuel_type])
                    current, capacity = cursor.fetchone()
                    if current is not None and capacity is not None and capacity > 0:
                        fuel_levels[fuel_type] = {
                            'current': current,
                            'capacity': capacity,
                            'percentage': round((current / capacity) * 100, 1)
                        }
            except Exception as e:
                print(f"Error fetching fuel levels for {fuel_type}: {e}")
    except Exception as e:
        print(f"Error fetching station data: {e}")
        total_stations = 0
        fuel_levels = {}

    # Get recent notifications
    try:
        recent_notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        recent_notifications = []

    # Prepare chart data
    dispatch_chart_data = []
    for i in range(30):
        date = (today - timedelta(days=29-i)).strftime('%Y-%m-%d')
        dispatch_chart_data.append({
            'date': date,
            'count': dispatch_trend.get(date, 0)
        })

    # Prepare map data
    map_data = []

    # Try to get locations from database
    if recent_locations:
        for loc in recent_locations:
            try:
                map_data.append({
                    'vehicle_id': loc.vehicle_id,
                    'license_plate': loc.vehicle.license_plate,
                    'latitude': float(loc.latitude),
                    'longitude': float(loc.longitude),
                    'timestamp': loc.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'speed': loc.speed
                })
            except Exception as e:
                print(f"Error preparing map data for location {loc.id}: {e}")

    # If no locations found, add some sample data for demonstration
    if not map_data:
        # Sample data for Albania
        sample_locations = [
            {'vehicle_id': 1, 'license_plate': 'AA001BB', 'latitude': 41.3275, 'longitude': 19.8187, 'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'), 'speed': 65},  # Tirana
            {'vehicle_id': 2, 'license_plate': 'AA002BB', 'latitude': 41.3233, 'longitude': 19.4542, 'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'), 'speed': 0},   # Durres
            {'vehicle_id': 3, 'license_plate': 'AA003BB', 'latitude': 40.7075, 'longitude': 19.9533, 'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'), 'speed': 45},  # Fier
            {'vehicle_id': 4, 'license_plate': 'AA004BB', 'latitude': 42.0692, 'longitude': 19.5033, 'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'), 'speed': 72},  # Shkoder
            {'vehicle_id': 5, 'license_plate': 'AA005BB', 'latitude': 41.1167, 'longitude': 20.0833, 'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'), 'speed': 55},  # Elbasan
        ]
        map_data = sample_locations

    context = {
        # Vehicle statistics
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'maintenance_vehicles_count': maintenance_vehicles,
        'maintenance_vehicles': Vehicle.objects.filter(next_maintenance_date__lte=now)[:5],

        # Station statistics
        'total_stations': total_stations,
        'fuel_levels': fuel_levels,

        # Dispatch statistics
        'total_dispatches': sum(status_counts.values()) if status_counts else 0,
        'planned_dispatches': status_counts.get('PLANNED', 0),
        'in_progress_dispatches': status_counts.get('IN_PROGRESS', 0),
        'completed_dispatches': status_counts.get('COMPLETED', 0),
        'cancelled_dispatches': status_counts.get('CANCELLED', 0),
        'today_dispatches': today_dispatches,

        # Chart data
        'dispatch_chart_data': json.dumps(dispatch_chart_data, cls=DecimalEncoder),

        # Map data
        'map_data': json.dumps(map_data, cls=DecimalEncoder),

        # Notifications
        'recent_notifications': recent_notifications,

        # Date context
        'today': today,
        'now': now,
    }

    return render(request, 'dashboards/dashboard.html', context)
