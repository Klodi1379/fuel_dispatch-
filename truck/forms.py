from django import forms
from django.forms import inlineformset_factory
from .models import Vehicle, Compartment

class CompartmentForm(forms.ModelForm):
    class Meta:
        model = Compartment
        fields = ['capacity']

# Krijo një formset për kompartimentet që janë të lidhura me një veturë
VehicleCompartmentFormset = inlineformset_factory(
    Vehicle, Compartment, form=CompartmentForm,
    extra=1, can_delete=True)  # 'extra' është numri i formave të reja të zbrazëta që të shfaqen



class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['license_plate', 'chassis_number', 'compartment_number', 'separated_cab', 'has_pump', 'hose_length', 'free_flow_unloading']