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

class LoadForm(forms.ModelForm):
    class Meta:
        model = Load
        fields = ['compartment', 'fuel_type', 'quantity']
        widgets = {
            'compartment': forms.Select(attrs={'class': 'form-control'}),
            'fuel_type': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
