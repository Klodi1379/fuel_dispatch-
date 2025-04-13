from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Notification, NotificationSetting, NotificationType, NotificationEvent
from .services import NotificationService

@login_required
def notification_list(request):
    """Shfaq listën e njoftimeve për përdoruesin e loguar"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    return render(request, 'notifications/list.html', context)

@login_required
def notification_detail(request, notification_id):
    """Shfaq detajet e një njoftimi"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)

    # Sheno njoftimin si të lexuar nëse nuk është
    if not notification.is_read:
        notification.is_read = True
        notification.save()

        # Regjistro ngjarjen e leximit
        NotificationEvent.objects.create(
            notification=notification,
            event_type='READ'
        )

    context = {
        'notification': notification
    }
    return render(request, 'notifications/detail.html', context)

@login_required
@require_POST
def mark_as_read(request, notification_id):
    """Sheno një njoftim si të lexuar"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()

    # Regjistro ngjarjen e leximit
    NotificationEvent.objects.create(
        notification=notification,
        event_type='READ'
    )

    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def mark_all_as_read(request):
    """Sheno të gjitha njoftimet si të lexuara"""
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)

    for notification in notifications:
        notification.is_read = True
        notification.save()

        # Regjistro ngjarjen e leximit
        NotificationEvent.objects.create(
            notification=notification,
            event_type='READ'
        )

    return JsonResponse({'status': 'success', 'count': notifications.count()})

@login_required
def notification_settings(request):
    """Shfaq dhe përditëson konfigurimet e njoftimeve"""
    notification_types = NotificationType.objects.all()
    user_settings = NotificationSetting.objects.filter(user=request.user)

    # Krijo settings për llojet e reja të njoftimeve nëse nuk ekzistojnë
    for notification_type in notification_types:
        if not user_settings.filter(notification_type=notification_type).exists():
            NotificationSetting.objects.create(
                user=request.user,
                notification_type=notification_type,
                is_enabled=True,
                notification_method='ALL'
            )

    # Merr settings e përditësuara
    user_settings = NotificationSetting.objects.filter(user=request.user)

    if request.method == 'POST':
        for setting in user_settings:
            setting_id = str(setting.id)
            is_enabled = setting_id in request.POST.getlist('enabled_notifications')
            method = request.POST.get(f'method_{setting_id}', 'ALL')

            setting.is_enabled = is_enabled
            setting.notification_method = method
            setting.save()

        messages.success(request, 'Konfigurimet e njoftimeve u përditësuan me sukses.')
        return redirect('notifications:settings')

    context = {
        'notification_types': notification_types,
        'user_settings': user_settings
    }
    return render(request, 'notifications/settings.html', context)
