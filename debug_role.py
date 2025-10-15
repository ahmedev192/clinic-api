import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath('clinic_management_system/final_working_test.py')))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_management_system.settings')
django.setup()

from apps.staff_management.models import Role
from django.contrib.auth import get_user_model

User = get_user_model()

# Clean database first
Role.objects.all().delete()
User.objects.all().delete()

# Create user
user = User.objects.create_user(
    email='test@clinic.com',
    password='testpass123',
    first_name='Test',
    last_name='User',
    username='test@clinic.com'
)

# Try to create role
try:
    role, created = Role.objects.get_or_create(
        code='DOC',
        defaults={
            'name_en': 'Doctor',
            'name_ar': 'طبيب',
            'description_en': 'Medical doctor role',
            'description_ar': 'دور الطبيب',
            'is_active': True
        }
    )
    print(f'Role created: {created}, Role: {role}')
except Exception as e:
    print(f'Error creating role: {e}')

# Try to create another role with same code
try:
    role2, created2 = Role.objects.get_or_create(
        code='DOC',
        defaults={
            'name_en': 'Doctor',
            'name_ar': 'طبيب',
            'description_en': 'Medical doctor role',
            'description_ar': 'دور الطبيب',
            'is_active': True
        }
    )
    print(f'Second role created: {created2}, Role: {role2}')
except Exception as e:
    print(f'Error creating second role: {e}')
