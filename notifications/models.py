from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class NotificationType(models.Model):
    """Llojet e njoftimeve që sistemi mund të gjenerojë"""

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class NotificationTemplate(models.Model):
    """Template për njoftimet (subjekt, përmbajtje, etj.)"""

    notification_type = models.OneToOneField(NotificationType, on_delete=models.CASCADE, related_name='template')
    subject_template = models.CharField(max_length=255)
    email_template = models.TextField()
    sms_template = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Template për {self.notification_type}"

class NotificationSetting(models.Model):
    """Konfigurimet e njoftimeve për çdo përdorues"""

    NOTIFICATION_METHODS = [
        ('EMAIL', 'Email'),
        ('IN_APP', 'In-App'),
        ('SMS', 'SMS'),
        ('ALL', 'Të gjitha')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_settings')
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)
    notification_method = models.CharField(max_length=10, choices=NOTIFICATION_METHODS, default='ALL')

    class Meta:
        unique_together = ['user', 'notification_type']

    def __str__(self):
        return f"{self.user.username} - {self.notification_type}"

class Notification(models.Model):
    """Njoftime të krijuara në sistem"""

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Për lidhjen me objekte të ndryshme (p.sh. FuelStation, Vehicle, etj.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} për {self.recipient.username}"

class NotificationEvent(models.Model):
    """Historia e ngjarjeve të njoftimeve (p.sh. dërgim, lexim)"""

    EVENT_TYPES = [
        ('CREATED', 'Krijuar'),
        ('SENT_EMAIL', 'Email i dërguar'),
        ('SENT_SMS', 'SMS i dërguar'),
        ('READ', 'Lexuar'),
        ('CLICKED', 'Klikuar')
    ]

    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=15, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.notification} - {self.get_event_type_display()} në {self.timestamp}"
