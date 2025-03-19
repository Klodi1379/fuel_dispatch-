from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from truck.models import Vehicle
from fuelstation.models import FuelStation
from dispatch.models import Dispatch

@login_required
def dashboard(request):
    context = {
        'total_vehicles': Vehicle.objects.count(),
        'total_stations': FuelStation.objects.count(),
        'total_dispatches': Dispatch.objects.count(),
        'today_dispatches': Dispatch.objects.filter(created_at__date=timezone.now().date()),
        'maintenance_vehicles': Vehicle.objects.filter(next_maintenance_date__lte=timezone.now()),
    }
    return render(request, 'dashboards/dashboard.html', context)
