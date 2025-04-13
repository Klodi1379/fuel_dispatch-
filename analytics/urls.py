from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('reports/', views.reports_list, name='reports'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('fuel-consumption/', views.fuel_consumption, name='fuel_consumption'),
    path('delivery-efficiency/', views.delivery_efficiency, name='delivery_efficiency'),
    path('fuel-prediction/', views.fuel_prediction, name='fuel_prediction'),
]
