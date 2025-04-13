from django.conf import settings
from django.core.mail import send_mail
from django.template import Template, Context
from django.contrib.auth.models import User
from django.db.models import Q, F
from django.contrib.contenttypes.models import ContentType
from .models import (
    Notification, NotificationType, NotificationEvent, 
    NotificationSetting, NotificationTemplate
)
from fuelstation.models import FuelTank
from truck.models import Vehicle
import datetime

class NotificationService:
    """Shërbimi për menaxhimin e njoftimeve"""
    
    @staticmethod
    def send_notification(user, notification_type_code, context_data, related_object=None):
        """
        Krijon dhe dërgon një njoftim
        
        Args:
            user: Përdoruesi që merr njoftimin
            notification_type_code: Kodi i llojit të njoftimit
            context_data: Dictionary me të dhëna për template
            related_object: Objekti i lidhur me njoftimin (opsional)
        
        Returns:
            Notification object or None if failed
        """
        try:
            # Kontrollo nëse përdoruesi ka aktivizuar këtë lloj njoftimi
            notification_type = NotificationType.objects.get(code=notification_type_code)
            
            # Kontrollo nëse përdoruesi e ka çaktivizuar këtë lloj njoftimi
            user_setting = NotificationSetting.objects.filter(
                user=user,
                notification_type=notification_type
            ).first()
            
            if user_setting and not user_setting.is_enabled:
                return None
            
            # Merr template
            template = notification_type.template
            
            # Përpuno temën dhe mesazhin
            subject_template = Template(template.subject_template)
            email_template = Template(template.email_template)
            
            ctx = Context(context_data)
            subject = subject_template.render(ctx)
            message = email_template.render(ctx)
            
            # Krijo njoftimin
            notification = Notification.objects.create(
                recipient=user,
                notification_type=notification_type,
                subject=subject,
                message=message
            )
            
            # Lidhe me objektin nëse është dhënë
            if related_object:
                notification.content_type = ContentType.objects.get_for_model(related_object)
                notification.object_id = related_object.id
                notification.save()
            
            # Regjistro ngjarjen e krijimit
            NotificationEvent.objects.create(
                notification=notification,
                event_type='CREATED'
            )
            
            # Dërgo njoftimin sipas preferencave të përdoruesit
            method = user_setting.notification_method if user_setting else 'ALL'
            
            if method in ['EMAIL', 'ALL'] and user.email:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                
                NotificationEvent.objects.create(
                    notification=notification,
                    event_type='SENT_EMAIL'
                )
            
            return notification
            
        except Exception as e:
            print(f"Gabim gjatë dërgimit të njoftimit: {e}")
            return None
    
    @staticmethod
    def check_low_fuel_levels():
        """Kontrollon për nivele të ulëta karburanti dhe dërgon njoftime"""
        
        low_tanks = FuelTank.objects.filter(
            current_level__lt=(F('capacity') * 0.2)  # Më pak se 20% e kapacitetit
        )
        
        for tank in low_tanks:
            # Gjej përdoruesit që duhet të njoftohen (admin dhe menaxherë)
            admins = User.objects.filter(
                Q(is_superuser=True) | 
                Q(groups__name='Fuel Managers')
            ).distinct()
            
            for admin in admins:
                NotificationService.send_notification(
                    user=admin,
                    notification_type_code='LOW_FUEL_LEVEL',
                    context_data={
                        'station_name': tank.fuel_station.name,
                        'fuel_type': tank.get_fuel_type_display(),
                        'current_level': tank.current_level,
                        'capacity': tank.capacity,
                        'percentage': (tank.current_level / tank.capacity) * 100
                    },
                    related_object=tank
                )
    
    @staticmethod
    def check_vehicle_maintenance():
        """Kontrollon për automjete që kanë nevojë për mirëmbajtje dhe dërgon njoftime"""
        
        today = datetime.date.today()
        upcoming_maintenance = Vehicle.objects.filter(
            next_maintenance_date__lte=today + datetime.timedelta(days=7),
            is_active=True
        )
        
        for vehicle in upcoming_maintenance:
            # Njofto menaxherët e flotës
            managers = User.objects.filter(groups__name='Fleet Managers').distinct()
            
            for manager in managers:
                NotificationService.send_notification(
                    user=manager,
                    notification_type_code='MAINTENANCE_DUE',
                    context_data={
                        'vehicle': str(vehicle),
                        'license_plate': vehicle.license_plate,
                        'maintenance_date': vehicle.next_maintenance_date.strftime('%d/%m/%Y')
                    },
                    related_object=vehicle
                )
