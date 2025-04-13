from django.contrib import admin
from .models import Report, ReportData, FuelConsumptionStat, DeliveryPerformanceStat

class ReportDataInline(admin.TabularInline):
    model = ReportData
    extra = 0
    readonly_fields = ('generated_at', 'data', 'chart_config')
    can_delete = False

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'created_by', 'created_at', 'is_scheduled')
    list_filter = ('report_type', 'is_scheduled', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_by', 'created_at')
    inlines = [ReportDataInline]

@admin.register(FuelConsumptionStat)
class FuelConsumptionStatAdmin(admin.ModelAdmin):
    list_display = ('fuel_station', 'fuel_type', 'date', 'quantity_delivered', 'quantity_sold')
    list_filter = ('fuel_type', 'date', 'fuel_station')
    date_hierarchy = 'date'

@admin.register(DeliveryPerformanceStat)
class DeliveryPerformanceStatAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_dispatches', 'completed_on_time', 'delayed_deliveries', 'average_dispatch_time')
    list_filter = ('date',)
    date_hierarchy = 'date'
