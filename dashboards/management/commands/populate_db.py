import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from truck.models import Vehicle, Compartment
from fuelstation.models import FuelStation, FuelTank
from dispatch.models import Dispatch, Load
from tracking.models import VehicleLocation, Route
from notifications.models import Notification, NotificationSetting, NotificationType, NotificationEvent

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating database with sample data...')

        # Create users if they don't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        if not User.objects.filter(username='driver1').exists():
            User.objects.create_user('driver1', 'driver1@example.com', 'driver1')
            self.stdout.write(self.style.SUCCESS('Created driver1 user'))

        if not User.objects.filter(username='driver2').exists():
            User.objects.create_user('driver2', 'driver2@example.com', 'driver2')
            self.stdout.write(self.style.SUCCESS('Created driver2 user'))

        # Create vehicles
        self.create_vehicles()

        # Create fuel stations
        self.create_fuel_stations()

        # Create dispatches
        self.create_dispatches()

        # Create vehicle locations
        self.create_vehicle_locations()

        # Create notifications
        self.create_notifications()

        self.stdout.write(self.style.SUCCESS('Successfully populated database'))

    def create_vehicles(self):
        # Create vehicles if there are fewer than 10
        if Vehicle.objects.count() < 10:
            vehicle_types = ['TANKER', 'TRUCK', 'TRAILER']

            for i in range(1, 11):
                license_plate = f'AA{i:03d}BB'
                chassis_number = f'CHASSIS{i:05d}'

                # Check if vehicle already exists
                if Vehicle.objects.filter(license_plate=license_plate).exists() or \
                   Vehicle.objects.filter(chassis_number=chassis_number).exists():
                    self.stdout.write(f'Vehicle with license plate {license_plate} or chassis number {chassis_number} already exists. Skipping.')
                    continue

                vehicle_type = random.choice(vehicle_types)
                compartment_count = random.randint(1, 5) if vehicle_type == 'TANKER' else 1

                # Create vehicle
                vehicle = Vehicle.objects.create(
                    license_plate=license_plate,
                    chassis_number=chassis_number,
                    vehicle_type=vehicle_type,
                    compartment_number=compartment_count,
                    separated_cab=random.choice([True, False]),
                    has_pump=random.choice([True, False]),
                    hose_length=random.randint(5, 20) if random.choice([True, False]) else None,
                    free_flow_unloading=random.choice([True, False]),
                    year_of_manufacture=random.randint(2010, 2023),
                    last_maintenance_date=timezone.now().date() - timedelta(days=random.randint(30, 180)),
                    next_maintenance_date=timezone.now().date() + timedelta(days=random.randint(-10, 90)),
                    is_active=random.random() > 0.2,  # 80% chance of being active
                    notes=f'Sample vehicle {i} notes'
                )

                # Create compartments for the vehicle
                for j in range(1, compartment_count + 1):
                    Compartment.objects.create(
                        vehicle=vehicle,
                        compartment_number=j,
                        capacity=random.randint(1000, 5000),
                        is_active=random.random() > 0.1  # 90% chance of being active
                    )

                self.stdout.write(f'Created vehicle {vehicle.license_plate}')

    def create_fuel_stations(self):
        # Create fuel stations if there are fewer than 5
        if FuelStation.objects.count() < 5:
            cities = ['Tirana', 'Durres', 'Vlore', 'Shkoder', 'Elbasan']

            for i, city in enumerate(cities, 1):
                station_name = f'{city} Fuel Station'

                # Check if station already exists
                if FuelStation.objects.filter(name=station_name).exists():
                    self.stdout.write(f'Fuel station {station_name} already exists. Skipping.')
                    continue

                # Create fuel station directly
                try:
                    # Try to create the station without using created_at and updated_at
                    station = FuelStation()
                    station.name = station_name
                    station.address = f'{random.randint(1, 100)} Main St, {city}'
                    station.location = f'{city}, Albania'

                    # Save without using the created_at and updated_at fields
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO fuelstation_fuelstation (name, address, location) VALUES (?, ?, ?)",
                            [station.name, station.address, station.location]
                        )

                        # Get the ID of the inserted station
                        cursor.execute("SELECT last_insert_rowid()")
                        station_id = cursor.fetchone()[0]
                        station.id = station_id
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating fuel station: {e}'))
                    continue

                # Create fuel tanks for the station
                fuel_types = ['DIESEL', 'GASOLINE_95', 'GASOLINE_98']
                for fuel_type in fuel_types:
                    capacity = random.randint(10000, 50000)
                    current_level = random.randint(int(capacity * 0.1), int(capacity * 0.9))

                    FuelTank.objects.create(
                        station=station,
                        fuel_type=fuel_type,
                        capacity=capacity,
                        current_level=current_level
                    )

                self.stdout.write(f'Created fuel station {station.name}')

    def create_dispatches(self):
        # Create dispatches if there are fewer than 50
        if Dispatch.objects.count() < 50:
            # Get vehicles using raw SQL
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, license_plate FROM truck_vehicle
                    WHERE vehicle_type = 'TANKER' AND is_active = 1
                """)
                vehicles = [{'id': row[0], 'license_plate': row[1]} for row in cursor.fetchall()]

                # Get stations using raw SQL
                cursor.execute("SELECT id, name FROM fuelstation_fuelstation")
                stations = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

                # Get drivers
                drivers = list(User.objects.filter(username__startswith='driver'))

            if not vehicles or not stations:
                self.stdout.write(self.style.WARNING('No vehicles or stations available for creating dispatches'))
                return

            statuses = ['PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']
            status_weights = [0.3, 0.2, 0.4, 0.1]  # Probabilities for each status

            # Create dispatches over the last 30 days
            for i in range(50):
                days_ago = random.randint(0, 30)
                dispatch_date = timezone.now() - timedelta(days=days_ago)

                status = random.choices(statuses, weights=status_weights)[0]

                # Adjust date based on status
                if status == 'COMPLETED':
                    completion_date = dispatch_date + timedelta(hours=random.randint(2, 8))
                elif status == 'IN_PROGRESS':
                    dispatch_date = timezone.now() - timedelta(hours=random.randint(1, 4))
                    completion_date = None
                elif status == 'CANCELLED':
                    completion_date = dispatch_date + timedelta(hours=random.randint(1, 3))
                else:  # PLANNED
                    if days_ago == 0:
                        dispatch_date = timezone.now() + timedelta(hours=random.randint(1, 24))
                    completion_date = None

                # Select random vehicle and station
                vehicle = random.choice(vehicles)
                station = random.choice(stations)
                driver = random.choice(drivers) if random.random() > 0.1 else None  # 10% chance of no driver

                # Create dispatch using raw SQL
                try:
                    with connection.cursor() as cursor:
                        # Insert dispatch
                        cursor.execute("""
                            INSERT INTO dispatch_dispatch
                            (vehicle_id, fuel_station_id, driver_id, dispatch_date, status, completion_date, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, [
                            vehicle['id'],
                            station['id'],
                            driver.id if driver else None,
                            dispatch_date.strftime('%Y-%m-%d %H:%M:%S'),
                            status,
                            completion_date.strftime('%Y-%m-%d %H:%M:%S') if completion_date else None,
                            f'Sample dispatch {i+1}'
                        ])

                        # Get the ID of the inserted dispatch
                        cursor.execute("SELECT last_insert_rowid()")
                        dispatch_id = cursor.fetchone()[0]

                        # Create loads for the dispatch if status is IN_PROGRESS or COMPLETED
                        if status in ['IN_PROGRESS', 'COMPLETED']:
                            # Get compartments for the vehicle
                            cursor.execute("""
                                SELECT id, capacity FROM truck_compartment
                                WHERE vehicle_id = ? AND is_active = 1
                            """, [vehicle['id']])
                            compartments = [{'id': row[0], 'capacity': row[1]} for row in cursor.fetchall()]

                            for compartment in compartments:
                                if random.random() > 0.3:  # 70% chance of having a load
                                    fuel_type = random.choice(['DIESEL', 'GASOLINE_95', 'GASOLINE_98'])
                                    quantity = random.randint(int(compartment['capacity'] * 0.5), int(compartment['capacity'] * 0.95))

                                    # Insert load
                                    cursor.execute("""
                                        INSERT INTO dispatch_load
                                        (dispatch_id, compartment_id, fuel_type, quantity)
                                        VALUES (?, ?, ?, ?)
                                    """, [dispatch_id, compartment['id'], fuel_type, quantity])

                    self.stdout.write(f'Created dispatch {dispatch_id} with status {status}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating dispatch: {e}'))

    def create_vehicle_locations(self):
        # Create vehicle locations for active vehicles
        from django.db import connection

        # Get active vehicles using raw SQL
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, license_plate FROM truck_vehicle
                WHERE is_active = 1
            """)
            vehicles = [{'id': row[0], 'license_plate': row[1]} for row in cursor.fetchall()]

        # Base coordinates (approximate center of Albania)
        base_lat, base_lng = 41.3275, 19.8187

        for vehicle in vehicles:
            # Create a route for the vehicle
            try:
                with connection.cursor() as cursor:
                    # Insert route
                    end_location = random.choice(['Durres Port', 'Vlore Terminal', 'Shkoder Station', 'Elbasan Depot'])
                    cursor.execute("""
                        INSERT INTO tracking_route
                        (vehicle_id, name, start_location, end_location)
                        VALUES (?, ?, ?, ?)
                    """, [
                        vehicle['id'],
                        f'Route for {vehicle["license_plate"]}',
                        'Tirana Depot',
                        end_location
                    ])

                    # Get the ID of the inserted route
                    cursor.execute("SELECT last_insert_rowid()")
                    route_id = cursor.fetchone()[0]

                    # Create locations along the route
                    num_points = random.randint(5, 20)

                    for i in range(num_points):
                        # Create a location point with some randomness
                        hours_ago = random.randint(0, 24)
                        timestamp = timezone.now() - timedelta(hours=hours_ago, minutes=random.randint(0, 59))

                        # Add some random variation to coordinates
                        lat_offset = random.uniform(-0.5, 0.5)
                        lng_offset = random.uniform(-0.5, 0.5)

                        # Insert location
                        cursor.execute("""
                            INSERT INTO tracking_vehiclelocation
                            (vehicle_id, route_id, latitude, longitude, timestamp, speed)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, [
                            vehicle['id'],
                            route_id,
                            str(base_lat + lat_offset),
                            str(base_lng + lng_offset),
                            timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            random.randint(0, 90)
                        ])

                self.stdout.write(f'Created {num_points} location points for vehicle {vehicle["license_plate"]}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating locations for vehicle {vehicle["license_plate"]}: {e}'))

    def create_notifications(self):
        # Create notification types first
        notification_types = [
            ('DISPATCH', 'Dispatch Update', 'Notifications about dispatch status changes'),
            ('MAINTENANCE', 'Maintenance Reminder', 'Reminders about vehicle maintenance'),
            ('FUEL_LEVEL', 'Fuel Level Alert', 'Alerts about low fuel levels'),
            ('SYSTEM', 'System Notification', 'System-wide notifications')
        ]

        for code, name, description in notification_types:
            NotificationType.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description
                }
            )

        # Create notification settings for all users
        users = User.objects.all()
        types = NotificationType.objects.all()

        for user in users:
            # Create notification settings for each type
            for notification_type in types:
                NotificationSetting.objects.update_or_create(
                    user=user,
                    notification_type=notification_type,
                    defaults={
                        'is_enabled': True,
                        'notification_method': random.choice(['EMAIL', 'IN_APP', 'ALL'])
                    }
                )

            # Create sample notifications
            for i in range(random.randint(3, 10)):
                notification_type = random.choice(list(types))
                days_ago = random.randint(0, 14)

                if notification_type.code == 'DISPATCH':
                    subject = 'Dispatch Update'
                    message = f'Dispatch #{random.randint(1, 100)} has been {random.choice(["created", "updated", "completed"])}'
                elif notification_type.code == 'MAINTENANCE':
                    subject = 'Maintenance Reminder'
                    message = f'Vehicle {random.choice(["AA001BB", "AA002BB", "AA003BB"])} is due for maintenance'
                elif notification_type.code == 'FUEL_LEVEL':
                    subject = 'Low Fuel Level Alert'
                    message = f'Fuel tank for {random.choice(["Diesel", "Gasoline 95", "Gasoline 98"])} at {random.choice(["Tirana", "Durres", "Vlore"])} station is below 20%'
                else:  # SYSTEM
                    subject = 'System Notification'
                    message = f'System maintenance scheduled for {(timezone.now() + timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")}'

                notification = Notification.objects.create(
                    recipient=user,
                    notification_type=notification_type,
                    subject=subject,
                    message=message,
                    is_read=random.random() > 0.5  # 50% chance of being read
                )

                # Create a notification event
                NotificationEvent.objects.create(
                    notification=notification,
                    event_type='CREATED',
                    details='Created by populate_db command'
                )

                # Add a read event for read notifications
                if notification.is_read:
                    NotificationEvent.objects.create(
                        notification=notification,
                        event_type='READ',
                        timestamp=notification.created_at + timedelta(hours=random.randint(1, 24))
                    )

            self.stdout.write(f'Created notifications for user {user.username}')
