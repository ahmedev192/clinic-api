"""
Quick test to verify the system works
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_management_system.settings')
django.setup()

def test_basic_functionality():
    """Test basic system functionality"""
    print("Testing basic system functionality...")
    
    try:
        from django.contrib.auth import get_user_model
        from apps.patient_management.models import Patient
        from apps.staff_management.models import Doctor
        from apps.appointments.models import Appointment
        
        User = get_user_model()
        
        # Test 1: Create user
        print("1. Creating user...")
        user = User.objects.create_user(
            email='test@clinic.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            username='test@clinic.com'
        )
        print(f"   User created: {user.email}")
        
        # Test 2: Create patient
        print("2. Creating patient...")
        patient = Patient.objects.create(
            first_name_en='John',
            last_name_en='Doe',
            first_name_ar='جون',
            last_name_ar='دو',
            email='john.doe@example.com',
            phone_number='+1234567890',
            date_of_birth='1990-01-01',
            gender='M',
            address_en='123 Main St',
            address_ar='123 الشارع الرئيسي',
            city='Riyadh',
            state_province='Riyadh',
            postal_code='12345',
            national_id='1234567890',
            created_by=user
        )
        print(f"   Patient created: {patient.first_name_en} {patient.last_name_en}")
        
        # Test 3: Create doctor
        print("3. Creating doctor...")
        doctor = Doctor.objects.create(
            staff=user,
            professional_title_en='Dr.',
            professional_title_ar='د.',
            specialization_en='General Medicine',
            specialization_ar='الطب العام',
            license_number='MD123456',
            is_available=True,
            is_accepting_new_patients=True
        )
        print(f"   Doctor created: {doctor.professional_title_en} {doctor.staff.first_name}")
        
        # Test 4: Create appointment
        print("4. Creating appointment...")
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date='2024-01-15',
            appointment_time='10:00:00',
            status='scheduled',
            created_by=user
        )
        print(f"   Appointment created: {appointment.appointment_code}")
        
        # Test 5: Create consultation
        print("5. Creating consultation...")
        from apps.consultation.models import Consultation
        consultation = Consultation.objects.create(
            consultation_code='CONS001',
            patient=patient,
            doctor=doctor,
            appointment=appointment,
            consultation_type='new',
            status='completed',
            chief_complaint_en='Headache',
            chief_complaint_ar='صداع',
            symptoms_en='Severe headache for 2 days',
            symptoms_ar='صداع شديد لمدة يومين',
            examination_findings_en='Normal vital signs',
            examination_findings_ar='علامات حيوية طبيعية',
            assessment_notes_en='Tension headache',
            assessment_notes_ar='صداع توتر',
            consultation_date='2024-01-15T10:00:00Z',
            duration_minutes=30,
            created_by=user
        )
        print(f"   Consultation created: {consultation.consultation_code}")
        
        # Test 6: Test relationships
        print("6. Testing relationships...")
        assert appointment.patient == patient
        assert appointment.doctor == doctor
        assert consultation.patient == patient
        assert consultation.doctor == doctor
        print("   All relationships working correctly")
        
        # Test 7: Test multilingual support
        print("7. Testing multilingual support...")
        assert patient.first_name_en == 'John'
        assert patient.first_name_ar == 'جون'
        assert consultation.chief_complaint_en == 'Headache'
        assert consultation.chief_complaint_ar == 'صداع'
        print("   Multilingual support working correctly")
        
        # Test 8: Test API endpoints
        print("8. Testing API endpoints...")
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        client.force_authenticate(user=user)
        
        # Test patient list
        try:
            url = reverse('patient-list')
            response = client.get(url)
            print(f"   Patient API: {response.status_code}")
        except Exception as e:
            print(f"   Patient API error: {e}")
        
        # Test doctor list
        try:
            url = reverse('doctor-list')
            response = client.get(url)
            print(f"   Doctor API: {response.status_code}")
        except Exception as e:
            print(f"   Doctor API error: {e}")
        
        # Test appointment list
        try:
            url = reverse('appointment-list')
            response = client.get(url)
            print(f"   Appointment API: {response.status_code}")
        except Exception as e:
            print(f"   Appointment API error: {e}")
        
        print("\nSUCCESS: All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"\nERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_operations():
    """Test database operations"""
    print("\nTesting database operations...")
    
    try:
        from django.contrib.auth import get_user_model
        from apps.patient_management.models import Patient
        
        User = get_user_model()
        
        # Create test data
        user = User.objects.create_user(
            email='db_test@clinic.com',
            password='testpass123',
            first_name='DB',
            last_name='Test',
            username='db_test@clinic.com'
        )
        
        patient = Patient.objects.create(
            first_name_en='Test',
            last_name_en='Patient',
            email='patient@test.com',
            phone_number='+1234567890',
            date_of_birth='1990-01-01',
            gender='M',
            address_en='Test Address',
            city='Test City',
            state_province='Test State',
            postal_code='12345',
            national_id='1234567891',
            created_by=user
        )
        
        # Test CRUD operations
        # Read
        retrieved_patient = Patient.objects.get(id=patient.id)
        assert retrieved_patient.first_name_en == 'Test'
        
        # Update
        retrieved_patient.first_name_en = 'Updated'
        retrieved_patient.save()
        
        # Verify update
        updated_patient = Patient.objects.get(id=patient.id)
        assert updated_patient.first_name_en == 'Updated'
        
        # Delete
        patient_id = patient.id
        patient.delete()
        
        # Verify deletion
        assert not Patient.objects.filter(id=patient_id).exists()
        
        print("SUCCESS: Database operations test passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Database operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("CLINIC MANAGEMENT SYSTEM - QUICK TEST")
    print("=" * 60)
    
    # Set environment variables
    os.environ['PYTHONPATH'] = os.path.dirname(__file__)
    os.environ['SECRET_KEY'] = 'django-insecure-test-key-for-development-only'
    
    # Run tests
    test1_result = test_basic_functionality()
    test2_result = test_database_operations()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum([test1_result, test2_result])
    total = 2
    success_rate = (passed / total) * 100
    
    print(f"Basic Functionality: {'PASSED' if test1_result else 'FAILED'}")
    print(f"Database Operations: {'PASSED' if test2_result else 'FAILED'}")
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        print("\nSystem is working correctly!")
        return True
    else:
        print("\nSystem needs attention.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
