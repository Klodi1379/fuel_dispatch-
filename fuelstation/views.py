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

class FuelStationDetailView(LoginRequiredMixin, DetailView):
    model = FuelStation
    template_name = 'fuelstation/fuelstation_detail.html'
    context_object_name = 'fuel_station'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add recent dispatches
        context['dispatches'] = self.object.dispatches.all().order_by('-dispatch_date')[:5]
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
