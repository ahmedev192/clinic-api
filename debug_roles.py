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

def test_role_creation_sequence():
    print("Testing role creation sequence...")
    
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
    
    # Test 1: Create role with code 'DOC_APP'
    print("Creating role with code 'DOC_APP'...")
    try:
        role1, created1 = Role.objects.get_or_create(
            code='DOC_APP',
            defaults={
                'name_en': 'Doctor',
                'name_ar': 'طبيب',
                'description_en': 'Medical doctor role',
                'description_ar': 'دور الطبيب',
                'is_active': True
            }
        )
        print(f"Role 1 created: {created1}, Role: {role1}")
    except Exception as e:
        print(f"Error creating role 1: {e}")
        return False
    
    # Test 2: Create role with code 'DOC_CON'
    print("Creating role with code 'DOC_CON'...")
    try:
        role2, created2 = Role.objects.get_or_create(
            code='DOC_CON',
            defaults={
                'name_en': 'Doctor',
                'name_ar': 'طبيب',
                'description_en': 'Medical doctor role',
                'description_ar': 'دور الطبيب',
                'is_active': True
            }
        )
        print(f"Role 2 created: {created2}, Role: {role2}")
    except Exception as e:
        print(f"Error creating role 2: {e}")
        return False
    
    # Test 3: Create role with code 'DOC_BILL'
    print("Creating role with code 'DOC_BILL'...")
    try:
        role3, created3 = Role.objects.get_or_create(
            code='DOC_BILL',
            defaults={
                'name_en': 'Doctor',
                'name_ar': 'طبيب',
                'description_en': 'Medical doctor role',
                'description_ar': 'دور الطبيب',
                'is_active': True
            }
        )
        print(f"Role 3 created: {created3}, Role: {role3}")
    except Exception as e:
        print(f"Error creating role 3: {e}")
        return False
    
    print("All role creations successful!")
    return True

if __name__ == "__main__":
    test_role_creation_sequence()
