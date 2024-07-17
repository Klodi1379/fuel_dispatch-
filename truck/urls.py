# urls.py
from django.urls import path
from .views import add_or_edit_vehicle, add_vehicle,VehicleListView, delete_vehicle, edit_vehicle

app_name='truck' 


urlpatterns = [
    path('add/vehicle/', add_vehicle, name='add_vehicle'),
    path('', VehicleListView.as_view(), name='vehicle_list'),
    path('edit/vehicle/<int:vehicle_id>/', edit_vehicle, name='edit_vehicle'),
    path('delete/vehicle/<int:vehicle_id>/', delete_vehicle, name='delete_vehicle'),
    
    path('vehicle/add/', add_or_edit_vehicle, name='add_vehicle'),
    
    # Rruga për editimin e një mjeti ekzistues (me ID)
    path('vehicle/edit/<int:vehicle_id>/', add_or_edit_vehicle, name='edit_vehicle'),
    
    
    
    

    # Shtoni rrugë të tjera sipas nevojës
]
