from django.contrib import admin
from .models import VehicleLocation, Route, RouteWaypoint

class RouteWaypointInline(admin.TabularInline):
    model = RouteWaypoint
    extra = 1

@admin.register(VehicleLocation)
class VehicleLocationAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'latitude', 'longitude', 'timestamp')
    list_filter = ('vehicle', 'timestamp')
    search_fields = ('vehicle__license_plate',)
    date_hierarchy = 'timestamp'

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('dispatch', 'start_location', 'end_location', 'status', 'estimated_distance', 'estimated_duration')
    list_filter = ('status', 'created_at')
    search_fields = ('dispatch__vehicle__license_plate',)
    inlines = [RouteWaypointInline]
