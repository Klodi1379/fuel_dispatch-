# admin.py
from django.contrib import admin
from .models import Vehicle, Compartment



class CompartmentInline(admin.TabularInline):
    model = Compartment
    extra = 1  # Numri i formave shtesë të dhomave për të shfaqur nga fillimi

class VehicleAdmin(admin.ModelAdmin):
    inlines = [CompartmentInline]

admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Compartment)  # Opsionale, nëse doni të menaxhoni kompartimentet direkt
