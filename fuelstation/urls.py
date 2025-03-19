from django.urls import path
from . import views

app_name = 'fuelstation'

urlpatterns = [
    path('', views.FuelStationListView.as_view(), name='fuelstation_list'),
    path('<int:pk>/', views.FuelStationDetailView.as_view(), name='fuelstation_detail'),
    path('add/', views.FuelStationCreateView.as_view(), name='fuelstation_add'),
    path('<int:pk>/edit/', views.FuelStationUpdateView.as_view(), name='fuelstation_edit'),
    path('<int:pk>/delete/', views.FuelStationDeleteView.as_view(), name='fuelstation_delete'),
]
