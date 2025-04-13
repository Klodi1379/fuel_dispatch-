from django.contrib import admin
from .models import NotificationType, NotificationTemplate, NotificationSetting, Notification, NotificationEvent

class NotificationTemplateInline(admin.StackedInline):
    model = NotificationTemplate
    can_delete = False

@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    inlines = [NotificationTemplateInline]

@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'is_enabled', 'notification_method')
    list_filter = ('is_enabled', 'notification_method', 'notification_type')
    search_fields = ('user__username', 'notification_type__name')

class NotificationEventInline(admin.TabularInline):
    model = NotificationEvent
    extra = 0
    readonly_fields = ('event_type', 'timestamp', 'details')
    can_delete = False

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'notification_type', 'created_at')
    search_fields = ('subject', 'message', 'recipient__username')
    readonly_fields = ('recipient', 'notification_type', 'subject', 'message', 'created_at')
    inlines = [NotificationEventInline]

@admin.register(NotificationEvent)
class NotificationEventAdmin(admin.ModelAdmin):
    list_display = ('notification', 'event_type', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('notification__subject', 'details')
    readonly_fields = ('notification', 'event_type', 'timestamp')
