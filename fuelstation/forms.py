from django import forms
from django.forms import inlineformset_factory
from .models import FuelStation, FuelTank

class FuelStationForm(forms.ModelForm):
    class Meta:
        model = FuelStation
        fields = ['name', 'address', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FuelTankForm(forms.ModelForm):
    class Meta:
        model = FuelTank
        fields = ['fuel_type', 'capacity']
        widgets = {
            'fuel_type': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Formset për menaxhimin e rezervuarëve të lidhur me një stacion
FuelTankFormset = inlineformset_factory(
    FuelStation, FuelTank, 
    form=FuelTankForm,
    extra=1, 
    can_delete=True
)
