from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Report, ReportData, FuelConsumptionStat, DeliveryPerformanceStat
from .report_service import ReportingService
from fuelstation.models import FuelStation

@login_required
def reports_list(request):
    """Shfaq listën e raporteve të ruajtura"""
    reports = Report.objects.all().order_by('-created_at')

    context = {
        'reports': reports
    }
    return render(request, 'analytics/reports_list.html', context)

@login_required
def report_detail(request, report_id):
    """Shfaq detajet e një raporti"""
    report = get_object_or_404(Report, id=report_id)
    report_data = report.data_sets.order_by('-generated_at').first()

    context = {
        'report': report,
        'report_data': report_data
    }
    return render(request, 'analytics/report_detail.html', context)

@login_required
def fuel_consumption(request):
    """Shfaq raportin e konsumit të karburantit"""
    # Vlerat default për filtrat
    today = timezone.now().date()
    default_start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    default_end_date = today.strftime('%Y-%m-%d')

    # Merr parametrat e filtrit
    start_date = request.GET.get('start_date', default_start_date)
    end_date = request.GET.get('end_date', default_end_date)
    station_id = request.GET.get('station_id')
    fuel_type = request.GET.get('fuel_type')

    # Gjenero raportin
    report_data = None
    if 'generate' in request.GET:
        report_data = ReportingService.generate_fuel_consumption_report(
            start_date=start_date,
            end_date=end_date,
            station_id=station_id,
            fuel_type=fuel_type
        )

        # Ruaj raportin nëse kërkohet
        if 'save_report' in request.GET and report_data['data']:
            title = request.GET.get('report_title', f"Konsumi i Karburantit {start_date} deri {end_date}")
            report = ReportingService.save_report(
                title=title,
                report_type='FUEL_CONSUMPTION',
                data=report_data['data'],
                chart_config=report_data['chart_config'],
                user=request.user,
                parameters={
                    'start_date': start_date,
                    'end_date': end_date,
                    'station_id': station_id,
                    'fuel_type': fuel_type
                }
            )
            messages.success(request, f"Raporti u ruajt me sukses me ID {report.id}")

    # Merr listën e stacioneve për filtrim
    try:
        # Use values() to specify exactly which fields to retrieve
        stations = FuelStation.objects.all().values('id', 'name', 'location')
    except Exception as e:
        print(f"Error fetching fuel stations: {e}")
        stations = []

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'station_id': station_id,
        'fuel_type': fuel_type,
        'stations': stations,
        'report_data': report_data
    }
    return render(request, 'analytics/fuel_consumption.html', context)

@login_required
def delivery_efficiency(request):
    """Shfaq raportin e efiçencës së dërgesave"""
    # Vlerat default për filtrat
    today = timezone.now().date()
    default_start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    default_end_date = today.strftime('%Y-%m-%d')

    # Merr parametrat e filtrit
    start_date = request.GET.get('start_date', default_start_date)
    end_date = request.GET.get('end_date', default_end_date)

    # Gjenero raportin
    report_data = None
    if 'generate' in request.GET:
        report_data = ReportingService.generate_delivery_efficiency_report(
            start_date=start_date,
            end_date=end_date
        )

        # Calculate statistics for the template
        if report_data and report_data['data']:
            times = [item['average_dispatch_time'] for item in report_data['data']]
            report_data['avg_time'] = round(sum(times) / len(times)) if times else 0
            report_data['max_time'] = max(times) if times else 0
            report_data['min_time'] = min(times) if times else 0

        # Ruaj raportin nëse kërkohet
        if 'save_report' in request.GET and report_data['data']:
            title = request.GET.get('report_title', f"Efiçenca e Dërgesave {start_date} deri {end_date}")
            report = ReportingService.save_report(
                title=title,
                report_type='DELIVERY_EFFICIENCY',
                data=report_data['data'],
                chart_config=report_data['chart_config'],
                user=request.user,
                parameters={
                    'start_date': start_date,
                    'end_date': end_date
                }
            )
            messages.success(request, f"Raporti u ruajt me sukses me ID {report.id}")

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'report_data': report_data
    }
    return render(request, 'analytics/delivery_efficiency.html', context)

@login_required
def fuel_prediction(request):
    """Shfaq parashikimet për nevojat e karburantit"""
    # Merr parametrat
    station_id = request.GET.get('station_id')
    days_ahead = int(request.GET.get('days_ahead', 7))

    # Merr listën e stacioneve
    try:
        # Use values() to specify exactly which fields to retrieve
        stations = FuelStation.objects.all().values('id', 'name', 'location')
    except Exception as e:
        print(f"Error fetching fuel stations: {e}")
        stations = []

    # Gjenero parashikimet
    prediction_data = None
    if station_id:
        prediction_data = ReportingService.predict_fuel_needs(
            station_id=station_id,
            days_ahead=days_ahead
        )

    context = {
        'stations': stations,
        'station_id': station_id,
        'days_ahead': days_ahead,
        'prediction_data': prediction_data
    }
    return render(request, 'analytics/fuel_prediction.html', context)
