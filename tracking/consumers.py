import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import VehicleLocation

class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "vehicle_tracking"
        self.room_group_name = f"tracking_{self.room_name}"
        
        # Bashkohu në grup
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Largo nga grupi
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Merr mesazhin nga WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'vehicle_location':
            vehicle_id = text_data_json.get('vehicle_id')
            latitude = text_data_json.get('latitude')
            longitude = text_data_json.get('longitude')
            
            # Ruaj vendndodhjen në databazë
            await self.save_location(vehicle_id, latitude, longitude)
            
            # Transmeto të dhënat tek të gjithë klientët
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location_update',
                    'vehicle_id': vehicle_id,
                    'latitude': latitude,
                    'longitude': longitude
                }
            )
    
    # Trajtimi i mesazhit të dërguar nga grupi
    async def location_update(self, event):
        vehicle_id = event['vehicle_id']
        latitude = event['latitude']
        longitude = event['longitude']
        
        # Dërgo mesazhin tek WebSocket
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'vehicle_id': vehicle_id,
            'latitude': latitude,
            'longitude': longitude
        }))
    
    @database_sync_to_async
    def save_location(self, vehicle_id, latitude, longitude):
        from truck.models import Vehicle
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            VehicleLocation.objects.create(
                vehicle=vehicle,
                latitude=latitude,
                longitude=longitude
            )
            return True
        except Exception as e:
            print(f"Gabim gjatë ruajtjes së vendndodhjes: {e}")
            return False
