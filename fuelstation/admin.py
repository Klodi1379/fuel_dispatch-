from django.contrib import admin
from .models import FuelStation, FuelTank

class FuelTankInline(admin.TabularInline):
    model = FuelTank
    extra = 1
    fields = ['station', 'fuel_type', 'capacity']  # Fushat nga modeli FuelTank

class FuelStationAdmin(admin.ModelAdmin):
    inlines = [FuelTankInline]
    fields = ['name', 'address', 'location']  # Fields from the FuelStation model
    list_display = ['name', 'address', 'location', 'fuel_type', 'capacity']

    def fuel_type(self, obj):
        return ', '.join([str(tank.fuel_type) for tank in obj.fuel_tanks.all()])

    def capacity(self, obj):
        return ', '.join([str(tank.capacity) for tank in obj.fuel_tanks.all()])
        

admin.site.register(FuelStation, FuelStationAdmin)

