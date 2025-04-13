from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from dashboards.views import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', dashboard, name='dashboard'),  # Dashboard si faqja kryesore
    path('truck/', include('truck.urls', namespace='truck')),
    path('fuelstation/', include('fuelstation.urls', namespace='fuelstation')),
    path('dispatch/', include('dispatch.urls', namespace='dispatch')),
    path('accounts/', include('accounts.urls')),
    path('dashboards/', include('dashboards.urls')),
    
    # URLs për autentikim
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('tracking/', include('tracking.urls')),
    path('notifications/', include('notifications.urls')),
    path('analytics/', include('analytics.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
