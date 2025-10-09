#!/usr/bin/env python
"""
Startup script for the Billing & Payments Module.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Start the Django development server."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'billing_payments.settings')
    django.setup()
    
    print("Starting Billing & Payments Module...")
    print("=" * 50)
    print("API Documentation: http://localhost:8000/api/docs/")
    print("Admin Panel: http://localhost:8000/admin/")
    print("API Base URL: http://localhost:8000/api/")
    print("=" * 50)
    
    # Run migrations
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create superuser if it doesn't exist
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        print("Creating admin user...")
        User.objects.create_superuser(
            username='admin',
            email='admin@clinic.com',
            password='admin123'
        )
        print("Admin user created: username=admin, password=admin123")
    
    # Seed initial data
    print("Seeding initial data...")
    execute_from_command_line(['manage.py', 'seed_data'])
    
    print("\nStarting development server...")
    execute_from_command_line(['manage.py', 'runserver'])

if __name__ == '__main__':
    main()
