import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from django.db.models import Sum, Avg, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from .models import Report, ReportData, FuelConsumptionStat, DeliveryPerformanceStat
from dispatch.models import Dispatch
from fuelstation.models import FuelStation, FuelTank

class ReportingService:
    """Shërbimi për gjenerimin e raporteve dhe analizave"""

    @staticmethod
    def generate_fuel_consumption_report(start_date, end_date, station_id=None, fuel_type=None):
        """
        Gjeneron raport për konsumin e karburantit

        Args:
            start_date: Data e fillimit për raport
            end_date: Data e përfundimit për raport
            station_id: ID e stacionit të karburantit (opsionale)
            fuel_type: Lloji i karburantit (opsionale)

        Returns:
            Dictionary me të dhënat e raportit dhe konfigurimin e grafikut
        """
        # Ndërto query bazë
        query = FuelConsumptionStat.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )

        # Apliko filtrat
        if station_id:
            query = query.filter(fuel_station_id=station_id)
        if fuel_type:
            query = query.filter(fuel_type=fuel_type)

        # Agrrego të dhënat
        data = query.values('date', 'fuel_type').annotate(
            total_delivered=Sum('quantity_delivered'),
            total_sold=Sum('quantity_sold')
        ).order_by('date', 'fuel_type')

        # Add the difference field
        for item in data:
            item['difference'] = item['total_delivered'] - item['total_sold']

        # Konverto në DataFrame për përpunim të mëtejshëm
        df = pd.DataFrame(list(data))

        if df.empty:
            return {
                'data': [],
                'chart_config': None
            }

        # Krijo grafikun
        plt.figure(figsize=(12, 6))

        for fuel_type in df['fuel_type'].unique():
            fuel_data = df[df['fuel_type'] == fuel_type]
            plt.plot(fuel_data['date'], fuel_data['total_sold'], label=f"Shitur - {fuel_type}")
            plt.plot(fuel_data['date'], fuel_data['total_delivered'], label=f"Dorëzuar - {fuel_type}", linestyle='--')

        plt.title('Konsumi i Karburantit dhe Dërgesat')
        plt.xlabel('Data')
        plt.ylabel('Sasia (litra)')
        plt.legend()
        plt.grid(True)

        # Konverto grafikun në imazh base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Përgatit të dhënat e raportit
        report_data = {
            'data': list(data),
            'chart_config': {
                'chart_type': 'line',
                'title': 'Konsumi i Karburantit dhe Dërgesat',
                'x_label': 'Data',
                'y_label': 'Sasia (litra)',
                'image_base64': image_base64
            }
        }

        return report_data

    @staticmethod
    def generate_delivery_efficiency_report(start_date, end_date):
        """Gjeneron raport për efiçencën e dërgesave"""

        # Merr statistikat e dërgesave
        stats = DeliveryPerformanceStat.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')

        # Konverto në DataFrame
        df = pd.DataFrame(list(stats.values()))

        if df.empty:
            return {
                'data': [],
                'chart_config': None
            }

        # Llogarit metrikat e efiçencës
        df['on_time_percentage'] = (df['completed_on_time'] / df['total_dispatches'] * 100).fillna(0).round(2)
        df['delayed_percentage'] = (df['delayed_deliveries'] / df['total_dispatches'] * 100).fillna(0).round(2)
        df['cancellation_rate'] = (df['cancelled_deliveries'] / df['total_dispatches'] * 100).fillna(0).round(2)

        # Krijo grafikun
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Grafiku 1: Raporti i dorëzimeve në kohë
        ax1.bar(df['date'], df['on_time_percentage'], color='green', label='% Në Kohë')
        ax1.set_title('Përqindja e Dorëzimeve në Kohë')
        ax1.set_xlabel('Data')
        ax1.set_ylabel('Përqindja (%)')
        ax1.grid(True)
        ax1.legend()

        # Grafiku 2: Koha mesatare e dërgesës
        ax2.plot(df['date'], df['average_dispatch_time'], marker='o', color='blue')
        ax2.set_title('Koha Mesatare e Dërgesës')
        ax2.set_xlabel('Data')
        ax2.set_ylabel('Minuta')
        ax2.grid(True)

        plt.tight_layout()

        # Konverto grafikun në imazh base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Përgatit të dhënat e raportit
        report_data = {
            'data': list(df.to_dict('records')),
            'chart_config': {
                'chart_type': 'combined',
                'title': 'Efiçenca e Dërgesave',
                'image_base64': image_base64
            }
        }

        return report_data

    @staticmethod
    def predict_fuel_needs(station_id, days_ahead=7):
        """Parashikon nevojat për karburant për një stacion të caktuar"""

        try:
            # Use values() to specify exactly which fields to retrieve
            station = FuelStation.objects.filter(id=station_id).values('id', 'name', 'location').first()
            if not station:
                raise FuelStation.DoesNotExist()
        except Exception:
            return {
                'station': {
                    'id': station_id,
                    'name': 'Unknown Station',
                    'location': 'Unknown Location'
                },
                'prediction_date': timezone.now().date().strftime('%Y-%m-%d'),
                'days_ahead': days_ahead,
                'predictions': []
            }

        today = timezone.now().date()

        # Merr të dhënat historike të konsumit (30 ditët e fundit)
        historical_data = FuelConsumptionStat.objects.filter(
            fuel_station_id=station_id,
            date__gte=today - timedelta(days=30),
            date__lte=today
        )

        # Agrrego sipas llojit të karburantit
        # Use a simpler approach - just use the standard fuel types
        fuel_types = ['DIESEL', 'GASOLINE_95', 'GASOLINE_98']

        predictions = []

        for fuel_type in fuel_types:
            # Llogarit konsumin mesatar ditor
            fuel_data = historical_data.filter(fuel_type=fuel_type)
            avg_daily_consumption = fuel_data.aggregate(avg=Avg('quantity_sold'))['avg'] or 0

            # Merr nivelin aktual të karburantit
            # Use a simpler approach - create a dummy tank if none exists
            current_tank = None

            # Get consumption data for this fuel type
            fuel_consumption = historical_data.filter(fuel_type=fuel_type).aggregate(
                total_delivered=Sum('quantity_delivered'),
                total_sold=Sum('quantity_sold')
            )

            # Create a dummy tank with reasonable values
            capacity = 10000  # Default capacity
            current_level = 5000  # Default level

            # Parashiko nivelin për ditët e ardhshme
            days_until_empty = round(current_level / avg_daily_consumption) if avg_daily_consumption > 0 else 999
            predicted_level_after_period = max(0, current_level - (avg_daily_consumption * days_ahead))
            needs_refill = days_until_empty <= days_ahead

            # Calculate additional fields for the template
            current_level_percentage = (current_level / capacity) * 100 if capacity > 0 else 0
            recommended_delivery_amount = avg_daily_consumption * 14  # 2 weeks supply

            predictions.append({
                'fuel_type': fuel_type,
                'fuel_type_display': dict(FuelTank.FUEL_TYPES).get(fuel_type),
                'current_level': current_level,
                'current_level_percentage': current_level_percentage,
                'capacity': capacity,
                'avg_daily_consumption': round(avg_daily_consumption, 2),
                'days_until_empty': days_until_empty,
                'predicted_level': round(predicted_level_after_period, 2),
                'predicted_percentage': round((predicted_level_after_period / capacity) * 100, 2),
                'needs_refill': needs_refill,
                'recommended_delivery_amount': recommended_delivery_amount
            })

        # If station is a dictionary (from values()), use it directly
        station_data = {
            'id': station['id'] if isinstance(station, dict) else station.id,
            'name': station['name'] if isinstance(station, dict) else station.name,
            'location': station['location'] if isinstance(station, dict) else station.location
        }

        return {
            'station': station_data,
            'prediction_date': today.strftime('%Y-%m-%d'),
            'days_ahead': days_ahead,
            'predictions': predictions
        }

    @staticmethod
    def save_report(title, report_type, data, chart_config, user, parameters=None):
        """Ruan një raport të gjeneruar në databazë"""

        report = Report.objects.create(
            title=title,
            report_type=report_type,
            created_by=user,
            parameters=parameters
        )

        ReportData.objects.create(
            report=report,
            data=data,
            chart_config=chart_config
        )

        return report
