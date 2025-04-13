#!/usr/bin/env python
import os
import time
import sys
import urllib.parse
from urllib.parse import urlparse

# Get the DATABASE_URL from environment
database_url = os.environ.get('DATABASE_URL', '')

if not database_url:
    print("No DATABASE_URL provided. Exiting.")
    sys.exit(0)

# Parse the DATABASE_URL
parsed_url = urlparse(database_url)

# If using SQLite, no need to wait
if parsed_url.scheme == 'sqlite':
    print("Using SQLite, no need to wait for database.")
    sys.exit(0)

# If using PostgreSQL, wait for it to be ready
if parsed_url.scheme == 'postgres' or parsed_url.scheme == 'postgresql':
    import psycopg2
    
    host = parsed_url.hostname
    port = parsed_url.port or 5432
    user = parsed_url.username
    password = parsed_url.password
    dbname = parsed_url.path[1:]  # Remove leading slash
    
    print(f"Waiting for PostgreSQL at {host}:{port}...")
    
    max_attempts = 30
    attempts = 0
    
    while attempts < max_attempts:
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname="postgres"  # Connect to default database first
            )
            conn.close()
            print("PostgreSQL is ready!")
            sys.exit(0)
        except psycopg2.OperationalError:
            attempts += 1
            print(f"PostgreSQL not ready yet (attempt {attempts}/{max_attempts})...")
            time.sleep(1)
    
    print("Could not connect to PostgreSQL after multiple attempts. Exiting.")
    sys.exit(1)

# If using another database type, add support here
print(f"Unsupported database type: {parsed_url.scheme}. Continuing without waiting.")
sys.exit(0)
