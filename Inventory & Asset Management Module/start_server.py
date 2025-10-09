#!/usr/bin/env python
"""
Startup script for Clinic Inventory & Asset Management Module
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Start the Django development server"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_inventory.settings')
    django.setup()
    
    print("Starting Clinic Inventory & Asset Management Module...")
    print("=" * 60)
    print("API Documentation:")
    print("  Swagger UI: http://localhost:8000/api/docs/")
    print("  ReDoc:      http://localhost:8000/api/redoc/")
    print("=" * 60)
    print("Admin Panel: http://localhost:8000/admin/")
    print("=" * 60)
    
    # Run migrations first
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create superuser if it doesn't exist
    from django.contrib.auth.models import User
    if not User.objects.filter(is_superuser=True).exists():
        print("\nNo superuser found. Creating one...")
        print("Username: admin")
        print("Email: admin@clinic.com")
        print("Password: admin123")
        User.objects.create_superuser('admin', 'admin@clinic.com', 'admin123')
        print("Superuser created successfully!")
    
    print("\nStarting development server...")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the server
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])

if __name__ == '__main__':
    main()
