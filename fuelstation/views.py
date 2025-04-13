from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import FuelStation, FuelTank
from .forms import FuelStationForm, FuelTankFormset

class FuelStationListView(LoginRequiredMixin, ListView):
    model = FuelStation
    template_name = 'fuelstation/fuelstation_list.html'
    context_object_name = 'fuel_stations'

    def get_queryset(self):
        # Use raw SQL to get fuel stations with tank counts
        from django.db import connection

        # Start with the base query
        query = "SELECT fs.id, fs.name, fs.address, fs.location, COUNT(ft.id) as tank_count "
        query += "FROM fuelstation_fuelstation fs "
        query += "LEFT JOIN fuelstation_fueltank ft ON fs.id = ft.station_id "
        query += "GROUP BY fs.id, fs.name, fs.address, fs.location"

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            stations_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Create a custom queryset
        from django.db.models.query import QuerySet
        queryset = QuerySet(model=FuelStation)
        queryset._result_cache = []

        # Create FuelStation objects with tank_count attribute
        for data in stations_data:
            station = FuelStation(id=data['id'],
                                 name=data['name'],
                                 address=data['address'],
                                 location=data['location'])

            # Add custom attributes
            station.tank_count = data['tank_count']

            queryset._result_cache.append(station)

        return queryset

class FuelStationDetailView(LoginRequiredMixin, DetailView):
    model = FuelStation
    template_name = 'fuelstation/fuelstation_detail.html'
    context_object_name = 'fuel_station'

    def get_object(self, queryset=None):
        # Get the station ID from the URL
        station_id = self.kwargs.get('pk')

        # Use raw SQL to get the station details
        from django.db import connection

        # Get the station details
        query = "SELECT id, name, address, location FROM fuelstation_fuelstation WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, [station_id])
            station_data = cursor.fetchone()

        if not station_data:
            from django.http import Http404
            raise Http404("No FuelStation found matching the query")

        # Create a FuelStation object
        station = FuelStation(id=station_data[0],
                             name=station_data[1],
                             address=station_data[2],
                             location=station_data[3])

        # Get the fuel tanks for this station
        query = "SELECT id, fuel_type, capacity FROM fuelstation_fueltank WHERE station_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, [station_id])
            tanks_data = cursor.fetchall()

        # Create FuelTank objects
        tanks = []
        for tank_data in tanks_data:
            tank = FuelTank(id=tank_data[0],
                           fuel_type=tank_data[1],
                           capacity=tank_data[2],
                           current_level=0,  # Default to 0 since column doesn't exist
                           fuel_station_id=station_id)
            tanks.append(tank)

        # Add the tanks to the station
        station._prefetched_objects_cache = {'fuel_tanks': tanks}

        return station

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get recent dispatches using raw SQL
        from django.db import connection

        query = "SELECT d.id, d.dispatch_date, d.status, v.license_plate "
        query += "FROM dispatch_dispatch d "
        query += "LEFT JOIN truck_vehicle v ON d.vehicle_id = v.id "
        query += "WHERE d.fuel_station_id = %s "
        query += "ORDER BY d.dispatch_date DESC LIMIT 5"

        with connection.cursor() as cursor:
            cursor.execute(query, [self.object.id])
            columns = [col[0] for col in cursor.description]
            dispatches_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Create dispatch objects
        from dispatch.models import Dispatch
        dispatches = []
        for data in dispatches_data:
            dispatch = Dispatch(id=data['id'],
                               dispatch_date=data['dispatch_date'],
                               status=data['status'])
            dispatch.vehicle_license_plate = data['license_plate']
            dispatches.append(dispatch)

        context['dispatches'] = dispatches
        return context

class FuelStationCreateView(LoginRequiredMixin, CreateView):
    model = FuelStation
    template_name = 'fuelstation/fuelstation_form.html'
    fields = ['name', 'address', 'location']
    success_url = reverse_lazy('fuelstation:fuelstation_list')

class FuelStationUpdateView(LoginRequiredMixin, UpdateView):
    model = FuelStation
    template_name = 'fuelstation/fuelstation_form.html'
    fields = ['name', 'address', 'location']
    success_url = reverse_lazy('fuelstation:fuelstation_list')

class FuelStationDeleteView(LoginRequiredMixin, DeleteView):
    model = FuelStation
    template_name = 'fuelstation/fuelstation_confirm_delete.html'
    success_url = reverse_lazy('fuelstation:fuelstation_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Fuel station deleted successfully!')
        return super().delete(request, *args, **kwargs)
