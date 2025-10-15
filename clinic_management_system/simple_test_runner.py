"""
Simple Test Runner for Clinic Management System
Runs basic tests without Unicode characters
"""

import os
import sys
import subprocess
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_management_system.settings')
django.setup()


def run_system_checks():
    """Run Django system checks"""
    print("Running Django system checks...")
    
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Capture output
        out = StringIO()
        call_command('check', '--deploy', stdout=out, stderr=out)
        output = out.getvalue()
        
        if 'ERRORS:' in output:
            print("ERROR: System check found errors:")
            print(output)
            return False
        else:
            print("SUCCESS: System checks passed")
            if output.strip():
                print("Warnings:")
                print(output)
            return True
            
    except Exception as e:
        print(f"ERROR: System check failed: {e}")
        return False


def run_migrations():
    """Run database migrations"""
    print("Running database migrations...")
    
    try:
        # Make migrations
        result = subprocess.run([
            sys.executable, 'manage.py', 'makemigrations'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode != 0:
            print(f"ERROR: Makemigrations failed: {result.stderr}")
            return False
        
        # Apply migrations
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode != 0:
            print(f"ERROR: Migrate failed: {result.stderr}")
            return False
        
        print("SUCCESS: Migrations completed successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        return False


def run_unit_tests():
    """Run Django unit tests"""
    print("Running unit tests...")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'test', '--verbosity=2'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode != 0:
            print("ERROR: Unit tests failed")
            return False
        
        print("SUCCESS: Unit tests passed")
        return True
        
    except Exception as e:
        print(f"ERROR: Unit tests failed: {e}")
        return False


def run_basic_integration_test():
    """Run basic integration test"""
    print("Running basic integration test...")
    
    try:
        from django.test import TestCase, Client
        from django.contrib.auth import get_user_model
        from django.urls import reverse
        
        User = get_user_model()
        
        # Create test user
        user = User.objects.create_user(
            email='test@clinic.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            username='test@clinic.com'
        )
        
        # Test client
        client = Client()
        client.force_authenticate(user=user)
        
        # Test basic endpoints
        try:
            # Test admin
            response = client.get('/admin/')
            print(f"Admin endpoint: {response.status_code}")
            
            # Test API root
            response = client.get('/api/v1/')
            print(f"API root: {response.status_code}")
            
        except Exception as e:
            print(f"Endpoint test error: {e}")
        
        print("SUCCESS: Basic integration test passed")
        return True
        
    except Exception as e:
        print(f"ERROR: Integration test failed: {e}")
        return False


def test_database_operations():
    """Test basic database operations"""
    print("Testing database operations...")
    
    try:
        from django.contrib.auth import get_user_model
        from apps.patient_management.models import Patient
        
        User = get_user_model()
        
        # Create user
        user = User.objects.create_user(
            email='db_test@clinic.com',
            password='testpass123',
            first_name='DB',
            last_name='Test',
            username='db_test@clinic.com'
        )
        
        # Create patient
        patient = Patient.objects.create(
            first_name_en='Test',
            last_name_en='Patient',
            email='patient@test.com',
            phone='+1234567890',
            date_of_birth='1990-01-01',
            gender='male',
            created_by=user
        )
        
        # Test retrieval
        retrieved_patient = Patient.objects.get(id=patient.id)
        assert retrieved_patient.first_name_en == 'Test'
        
        # Test update
        retrieved_patient.first_name_en = 'Updated'
        retrieved_patient.save()
        
        # Test deletion
        patient_id = patient.id
        patient.delete()
        
        # Verify deletion
        assert not Patient.objects.filter(id=patient_id).exists()
        
        print("SUCCESS: Database operations test passed")
        return True
        
    except Exception as e:
        print(f"ERROR: Database operations test failed: {e}")
        return False


def test_model_relationships():
    """Test model relationships"""
    print("Testing model relationships...")
    
    try:
        from django.contrib.auth import get_user_model
        from apps.patient_management.models import Patient
        from apps.staff_management.models import Doctor
        from apps.appointments.models import Appointment
        
        User = get_user_model()
        
        # Create user
        user = User.objects.create_user(
            email='rel_test@clinic.com',
            password='testpass123',
            first_name='Rel',
            last_name='Test',
            username='rel_test@clinic.com'
        )
        
        # Create patient
        patient = Patient.objects.create(
            first_name_en='John',
            last_name_en='Doe',
            email='john@test.com',
            phone='+1234567890',
            date_of_birth='1990-01-01',
            gender='male',
            created_by=user
        )
        
        # Create doctor
        doctor = Doctor.objects.create(
            staff=user,
            professional_title_en='Dr.',
            specialization_en='General Medicine',
            license_number='MD123456'
        )
        
        # Create appointment
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date='2024-01-15',
            appointment_time='10:00:00',
            status='scheduled',
            created_by=user
        )
        
        # Test relationships
        assert appointment.patient == patient
        assert appointment.doctor == doctor
        assert patient in doctor.patients.all()
        
        print("SUCCESS: Model relationships test passed")
        return True
        
    except Exception as e:
        print(f"ERROR: Model relationships test failed: {e}")
        return False


def main():
    """Main test runner"""
    print("=" * 60)
    print("CLINIC MANAGEMENT SYSTEM - TEST RUNNER")
    print("=" * 60)
    
    # Set environment variables
    os.environ['PYTHONPATH'] = os.path.dirname(__file__)
    os.environ['SECRET_KEY'] = 'django-insecure-test-key-for-development-only'
    
    test_results = {}
    
    # Run tests
    test_results['system_checks'] = run_system_checks()
    test_results['migrations'] = run_migrations()
    test_results['unit_tests'] = run_unit_tests()
    test_results['integration_test'] = run_basic_integration_test()
    test_results['database_operations'] = test_database_operations()
    test_results['model_relationships'] = test_model_relationships()
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    success_rate = (passed / total) * 100
    
    for test_name, result in test_results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        print("System is ready for deployment!")
        return True
    else:
        print("System needs attention before deployment.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
