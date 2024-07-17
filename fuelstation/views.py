from django.shortcuts import render, redirect, get_object_or_404
from .forms import FuelStationForm, FuelTankForm
from .models import FuelStation, FuelTank

def fuel_station_list(request):
    fuel_stations = FuelStation.objects.all()
    return render(request, 'fuel_stations/fuel_station_list.html', {'fuel_stations': fuel_stations})

def fuel_station_create(request):
    if request.method == 'POST':
        form = FuelStationForm(request.POST)
        if form.is_valid():
            fuel_station = form.save()
            return redirect('fuel_station_detail', pk=fuel_station.pk)
    else:
        form = FuelStationForm()
    return render(request, 'fuel_stations/fuel_station_form.html', {'form': form})

