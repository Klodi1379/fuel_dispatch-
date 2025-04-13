from django.utils import timezone
from .services import NotificationService

def check_notifications():
    """
    Task i planifikuar për të kontrolluar dhe dërguar njoftime
    Ky funksion duhet të thirret nga një cron job ose scheduler
    """
    # Kontrollo për nivele të ulëta karburanti
    NotificationService.check_low_fuel_levels()
    
    # Kontrollo për automjete që kanë nevojë për mirëmbajtje
    NotificationService.check_vehicle_maintenance()
    
    # Log-o ekzekutimin e task-ut
    print(f"[{timezone.now()}] Kontrolli i njoftimeve u ekzekutua me sukses")
