#!/usr/bin/env python
"""
Script to run the marker position tests
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TRUCK_DISPACHER.settings')
django.setup()

# Import the test runner
from django.test.runner import DiscoverRunner

def run_tests():
    """Run the marker position tests"""
    # Run the standard tests
    test_runner = DiscoverRunner(verbosity=2)
    failures = test_runner.run_tests(['tracking.tests.VehicleMarkerPositionTest'])
    
    if failures:
        print("Standard tests failed. Skipping Selenium tests.")
        return failures
    
    # Try to run the Selenium tests if available
    try:
        from selenium import webdriver
        print("\nRunning Selenium tests...")
        selenium_failures = test_runner.run_tests(['tracking.test_selenium'])
        return failures + selenium_failures
    except ImportError:
        print("\nSelenium not installed. Skipping browser tests.")
        print("To run browser tests, install Selenium: pip install selenium")
        return failures

if __name__ == '__main__':
    failures = run_tests()
    sys.exit(bool(failures))
