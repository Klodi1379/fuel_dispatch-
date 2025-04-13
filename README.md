# Fuel Dispatch System

This repository contains the code for the Fuel Dispatch System, which is designed to optimize the distribution of fuel supplies using various types of transport vehicles. The system involves different types of vehicles, discharge methods, and partitioned tanks for fuel distribution to geographically spread stations. The stations have varying storage needs and multiple product types like diesel, gas, and different octane gasoline.

## Features

- **Vehicle Management**: Add, edit, and delete vehicles in the system.
- **Fuel Station Management**: Manage fuel station details and fuel types.
- **Distribution Optimization**: Algorithms to optimize the distribution process.
- **Real-time Vehicle Tracking**: Track vehicles in real-time on a map.
- **Analytics and Reporting**: Generate reports and analyze data.
- **Notification System**: Receive notifications about important events.
- **User Authentication**: Secure user authentication and authorization.
- **Beautiful Dashboard**: Modern and informative dashboard.

## Installation with Docker

The easiest way to get started is using Docker and Docker Compose.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Klodi1379/fuel_dispatch-.git
   cd fuel_dispatch-
   ```

2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your settings.

4. Apply migrations manually (this is needed only once):
   ```bash
   # Apply migrations for auth and contenttypes first
   python manage.py migrate auth
   python manage.py migrate contenttypes

   # Apply migrations for notifications with --fake
   python manage.py migrate notifications --fake

   # Apply remaining migrations
   python manage.py migrate --fake-initial
   ```

5. Build and start the containers:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

6. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

7. Access the application at http://localhost:8000

## Development Setup

If you prefer to run the application without Docker:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at http://localhost:8000

## Project Structure

- `accounts/`: User authentication and profiles
- `analytics/`: Reporting and data analysis
- `dashboards/`: Main dashboard views
- `dispatch/`: Dispatch management
- `fuelstation/`: Fuel station management
- `notifications/`: Notification system
- `tracking/`: Vehicle tracking
- `truck/`: Vehicle management

## License

This project is licensed under the MIT License - see the LICENSE file for details.
