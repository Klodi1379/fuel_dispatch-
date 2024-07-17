# views.py
from django.shortcuts import render, redirect
from django.contrib import messages  # Shtoni këtë import

from .models import Vehicle

def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle added successfully!')  # Shtoni një mesazh të suksesshëm
            return redirect('vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'truck/add_vehicle.html', {'form': form})




# views.py
from django.views.generic import ListView
from .models import Vehicle

class VehicleListView(ListView):
    model = Vehicle
    template_name = 'truck/vehicle_list.html'
    context_object_name = 'vehicles'

from django.shortcuts import render, get_object_or_404, redirect
from .models import Vehicle


def edit_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect('truck:vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'truck/edit_vehicle.html', {'form': form, 'vehicle_id': vehicle_id})




from django.http import HttpResponseRedirect
from django.urls import reverse

def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if request.method == 'POST':
        vehicle.delete()
        return HttpResponseRedirect(reverse('truck:vehicle_list'))
    return render(request, 'truck/confirm_delete.html', {'vehicle': vehicle})

from django.shortcuts import render, redirect, get_object_or_404
from .forms import VehicleForm, VehicleCompartmentFormset

def add_or_edit_vehicle(request, vehicle_id=None):
    if vehicle_id:
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    else:
        vehicle = None

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        formset = VehicleCompartmentFormset(request.POST, instance=vehicle)

        if form.is_valid() and formset.is_valid():
            created_vehicle = form.save()  # Ruaj veturën
            formset.instance = created_vehicle
            formset.save()  # Ruaj kompartimentet
            return redirect('vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
        formset = VehicleCompartmentFormset(instance=vehicle)

    context = {
        'form': form,
        'formset': formset,
        'vehicle_id': vehicle_id
    }

    return render(request, 'truck/add_or_edit_vehicle.html', context)
