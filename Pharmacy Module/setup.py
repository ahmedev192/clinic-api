#!/usr/bin/env python
"""
Setup script for Pharmacy Management System
Run this script to set up the project for development
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🏥 Pharmacy Management System Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy.settings')
    django.setup()
    
    # Run migrations
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        print("❌ Failed to create migrations")
        sys.exit(1)
    
    if not run_command("python manage.py migrate", "Running migrations"):
        print("❌ Failed to run migrations")
        sys.exit(1)
    
    # Create superuser
    print("🔄 Creating superuser...")
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@pharmacy.com', 'admin123')
            print("✅ Superuser created: admin/admin123")
        else:
            print("✅ Superuser already exists")
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")
    
    # Create sample data
    if not run_command("python manage.py create_sample_data", "Creating sample data"):
        print("⚠️  Failed to create sample data, but setup can continue")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the development server: python manage.py runserver")
    print("2. Access the API documentation: http://localhost:8000/api/docs/")
    print("3. Access the admin interface: http://localhost:8000/admin/")
    print("4. Login with: admin/admin123")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
