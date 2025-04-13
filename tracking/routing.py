from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/tracking/', consumers.LocationConsumer.as_asgi()),
]
