#!/usr/bin/env python
"""
Simple debug script to check roles and fix the constraint issue
"""

import os
import sys
import django
from datetime import datetime

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_management_system.settings')
django.setup()

def check_roles():
    """Check existing roles in database"""
    try:
        from apps.staff_management.models import Role
        
        print("=== EXISTING ROLES ===")
        roles = Role.objects.all()
        for role in roles:
            print(f"Code: {role.code}, Name: {role.name_en}")
        
        print(f"Total roles: {roles.count()}")
        
        # Try to create a role with a unique code
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_code = f'DEBUG_{timestamp}'
        
        print(f"\n=== CREATING ROLE WITH CODE: {unique_code} ===")
        role, created = Role.objects.get_or_create(
            code=unique_code,
            defaults={
                'name_en': 'Debug Role',
                'name_ar': 'دور التصحيح',
                'description_en': 'Debug role for testing',
                'description_ar': 'دور التصحيح للاختبار',
                'is_active': True
            }
        )
        
        if created:
            print(f"SUCCESS: Created role {role.code}")
        else:
            print(f"EXISTS: Role {role.code} already exists")
            
        # Clean up
        role.delete()
        print("Cleaned up debug role")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_roles()
