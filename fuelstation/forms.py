from django.contrib import admin
from .models import FuelStation, FuelTank

class FuelTankInline(admin.TabularInline):
    model = FuelTank
    extra = 1
    fields = ['fuel_type', 'capacity']  # Fushat nga FuelTankForm

class FuelStationAdmin(admin.ModelAdmin):
    inlines = [FuelTankInline]
    fields = ['name', 'address', 'location']  # Fushat nga FuelStationForm

admin.site.register(FuelStation, FuelStationAdmin)
