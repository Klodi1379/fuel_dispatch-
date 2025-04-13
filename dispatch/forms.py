from django import forms
from .models import Dispatch, Load
from truck.models import Vehicle, Compartment
from fuelstation.models import FuelStation

class DispatchForm(forms.ModelForm):
    class Meta:
        model = Dispatch
        fields = ['vehicle', 'fuel_station', 'driver', 'dispatch_date', 'notes']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'fuel_station': forms.Select(attrs={'class': 'form-control'}),
            'driver': forms.Select(attrs={'class': 'form-control'}),
            'dispatch_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use a simpler approach to get fuel stations
        try:
            # Use raw SQL to get fuel stations without relying on the ORM
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name FROM fuelstation_fuelstation")
                stations = cursor.fetchall()

            # Create a queryset with the stations
            from django.db.models.query import QuerySet
            queryset = FuelStation.objects.none()

            # Add choices directly to the field
            self.fields['fuel_station'].choices = [(station[0], station[1]) for station in stations]
        except Exception as e:
            print(f"Error loading fuel stations: {e}")
            self.fields['fuel_station'].queryset = FuelStation.objects.none()

class LoadForm(forms.ModelForm):
    class Meta:
        model = Load
        fields = ['compartment', 'fuel_type', 'quantity']
        widgets = {
            'compartment': forms.Select(attrs={'class': 'form-control'}),
            'fuel_type': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
