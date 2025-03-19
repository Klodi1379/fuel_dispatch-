from django.contrib import admin
from .models import Dispatch, Load

class LoadInline(admin.TabularInline):
    model = Load
    extra = 1

class DispatchAdmin(admin.ModelAdmin):
    inlines = [LoadInline]
    list_display = ('id', 'vehicle', 'fuel_station', 'dispatch_date', 'status')
    list_filter = ('status', 'vehicle', 'fuel_station')
    search_fields = ('vehicle__license_plate', 'fuel_station__name')

admin.site.register(Dispatch, DispatchAdmin)
