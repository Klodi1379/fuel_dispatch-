from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'tracking'

router = DefaultRouter()
router.register(r'locations', views.VehicleLocationViewSet)
router.register(r'routes', views.RouteViewSet)

urlpatterns = [
    path('', views.tracking_dashboard, name='dashboard'),
    path('api/', include(router.urls)),
]
