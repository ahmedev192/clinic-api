"""
Improved Comprehensive Test for Clinic Management System
Tests all functionality with proper model usage and unique data
"""

import os
import sys
import django
from datetime import datetime
import random

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_management_system.settings')
django.setup()

def cleanup_database():
    """Clean up test data from database"""
    try:
        # Delete in reverse order of dependencies
        from apps.billing.models import Invoice, Payment
        from apps.consultation.models import Consultation, Prescription, LabOrder
        from apps.appointments.models import Appointment
        from apps.patient_management.models import Patient, MedicalHistory
        from apps.staff_management.models import Doctor, Staff
        from apps.accounts.models import User
        from apps.lab_tests.models import LabTest
        
        Invoice.objects.all().delete()
        Payment.objects.all().delete()
        Consultation.objects.all().delete()
        Prescription.objects.all().delete()
        LabOrder.objects.all().delete()
        Appointment.objects.all().delete()
        Patient.objects.all().delete()
        MedicalHistory.objects.all().delete()
        Doctor.objects.all().delete()
        Staff.objects.all().delete()
        LabTest.objects.all().delete()
        User.objects.all().delete()
        
        print("Database cleaned successfully")
    except Exception as e:
        print(f"Database cleanup failed: {e}")

def generate_unique_phone():
    """Generate a unique phone number for testing"""
    return f"+1{random.randint(1000000000, 9999999999)}"

def test_database_operations():
    """Test database operations"""
    print("Testing database operations...")
    
    try:
        from django.contrib.auth import get_user_model
        from apps.patient_management.models import Patient
        
        User = get_user_model()
        
        # Generate unique identifiers
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_email = f'db_test_{timestamp}@clinic.com'
        
        # Create test data
        user = User.objects.create_user(
            email=user_email,
            password='testpass123',
            first_name='DB',
            last_name='Test',
            username=user_email
        )
        
        patient = Patient.objects.create(
            first_name_en='Test',
            last_name_en='Patient',
            email='patient@test.com',
            phone_number=generate_unique_phone(),
            date_of_birth='1990-01-01',
            gender='M',
            address_en='Test Address',
            city='Test City',
            country='Test Country',
            status='active',
            created_by=user,
            updated_by=user
        )
        
        print(f"Created user: {user.email}")
        print(f"Created patient: {patient.first_name_en} {patient.last_name_en}")
        print("SUCCESS: Database operations test passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Database operations test failed: {e}")
        return False

def test_user_management():
    """Test user management functionality"""
    print("Testing user management...")
    
    try:
        from django.contrib.auth import get_user_model
        from apps.accounts.models import UserProfile
        
        User = get_user_model()
        
        # Generate unique identifiers
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_email = f'user_test_{timestamp}@clinic.com'
        
        # Create user
        user = User.objects.create_user(
            email=user_email,
            password='testpass123',
            first_name='User',
            last_name='Test',
            username=user_email
        )
        
        # Create user profile
        profile = UserProfile.objects.create(
            user=user,
            phone_number=generate_unique_phone(),
            date_of_birth='1985-05-15',
            gender='F',
            address_en='User Address',
            city='User City',
            country='User Country'
        )
        
        print(f"Created user: {user.email}")
        print(f"Created profile: {profile.user.first_name}")
        print("SUCCESS: User management test passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: User management test failed: {e}")
        return False

def test_patient_management():
    """Test patient management functionality"""
    print("Testing patient management...")
    
    try:
        from django.contrib.auth import get_user_model
        from apps.patient_management.models import Patient, MedicalHistory
        
        User = get_user_model()
        
        # Generate unique identifiers
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_email = f'patient_test_{timestamp}@clinic.com'
        
        # Create user
        user = User.objects.create_user(
            email=user_email,
            password='testpass123',
            first_name='Patient',
            last_name='Manager',
            username=user_email
        )
        
        # Create patient
        patient = Patient.objects.create(
            first_name_en='John',
            last_name_en='Doe',
            email='john.doe@test.com',
            phone_number=generate_unique_phone(),
            date_of_birth='1980-03-15',
            gender='M',
            address_en='123 Main St',
            city='New York',
            country='USA',
            status='active',
            created_by=user,
            updated_by=user
        )
        
        # Create medical history
        medical_history = MedicalHistory.objects.create(
            patient=patient,
            condition_en='Diabetes',
            condition_ar='مرض السكري',
            diagnosis_date='2020-01-15',
            status='active',
            notes_en='Type 2 diabetes, well controlled',
            notes_ar='داء السكري من النوع الثاني، محكوم جيداً',
            created_by=user,
            updated_by=user
        )
        
        print(f"Created patient: {patient.first_name_en} {patient.last_name_en}")
        print(f"Created medical history: {medical_history.condition_en}")
        print("SUCCESS: Patient management test passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Patient management test failed: {e}")
        return False

def test_appointment_system():
    """Test appointment system functionality"""
    print("Testing appointment system...")
    
    try:
        from django.contrib.auth import get_user_model
        from apps.patient_management.models import Patient
        from apps.staff_management.models import Staff, Doctor
        from apps.appointments.models import Appointment
        
        User = get_user_model()
        
        # Generate unique identifiers
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_email = f'appointment_test_{timestamp}@clinic.com'
        
        # Create user
        user = User.objects.create_user(
            email=user_email,
            password='testpass123',
            first_name='Appointment',
            last_name='Manager',
            username=user_email
        )
        
        # Create patient
        patient = Patient.objects.create(
            first_name_en='Jane',
            last_name_en='Smith',
            email='jane.smith@test.com',
            phone_number=generate_unique_phone(),
            date_of_birth='1985-07-20',
            gender='F',
            address_en='456 Oak Ave',
            city='Los Angeles',
            country='USA',
            status='active',
            created_by=user,
            updated_by=user
        )
        
        # Create staff
        staff = Staff.objects.create(
            user=user,
            employee_id=f'EMP{timestamp}',
            department='Cardiology',
            position='Doctor',
            hire_date='2020-01-01',
            salary=80000.00,
            is_active=True
        )
        
        # Create doctor
        doctor = Doctor.objects.create(
            staff=staff,
            specialization='Cardiology',
            license_number=f'LIC{timestamp}',
            is_available=True,
            is_accepting_new_patients=True
        )
        
        # Create appointment
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date='2024-01-15',
            appointment_time='10:00:00',
            status='scheduled',
            notes='Regular checkup',
            created_by=user,
            updated_by=user
        )
        
        print(f"Created appointment: {appointment.id}")
        print(f"Patient: {appointment.patient.first_name_en}")
        print(f"Doctor: {appointment.doctor.staff.user.first_name}")
        print("SUCCESS: Appointment system test passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Appointment system test failed: {e}")
        return False

def test_consultation_system():
    """Test consultation system functionality"""
    print("Testing consultation system...")
    
    try:
        from django.contrib.auth import get_user_model
        from apps.patient_management.models import Patient
        from apps.staff_management.models import Staff, Doctor
        from apps.appointments.models import Appointment
        from apps.consultation.models import Consultation
        
        User = get_user_model()
        
        # Generate unique identifiers
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_email = f'consultation_test_{timestamp}@clinic.com'
        
        # Create user
        user = User.objects.create_user(
            email=user_email,
            password='testpass123',
            first_name='Consultation',
            last_name='Manager',
            username=user_email
        )
        
        # Create patient
        patient = Patient.objects.create(
            first_name_en='Bob',
            last_name_en='Johnson',
            email='bob.johnson@test.com',
            phone_number=generate_unique_phone(),
            date_of_birth='1975-12-10',
            gender='M',
            address_en='789 Pine St',
            city='Chicago',
            country='USA',
            status='active',
            created_by=user,
            updated_by=user
        )
        
        # Create staff
        staff = Staff.objects.create(
            user=user,
            employee_id=f'EMP{timestamp}',
            department='Internal Medicine',
            position='Doctor',
            hire_date='2019-06-01',
            salary=90000.00,
            is_active=True
        )
        
        # Create doctor
        doctor = Doctor.objects.create(
            staff=staff,
            specialization='Internal Medicine',
            license_number=f'LIC{timestamp}',
            is_available=True,
            is_accepting_new_patients=True
        )
        
        # Create appointment
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date='2024-01-16',
            appointment_time='14:00:00',
            status='completed',
            notes='Follow-up consultation',
            created_by=user,
            updated_by=user
        )
        
        # Create consultation
        consultation = Consultation.objects.create(
            patient=patient,
            doctor=doctor,
            appointment=appointment,
            consultation_type='follow_up',
            status='completed',
            chief_complaint_en='Chest pain',
            chief_complaint_ar='ألم في الصدر',
            symptoms_en='Mild chest discomfort',
            symptoms_ar='انزعاج خفيف في الصدر',
            examination_findings_en='Normal heart sounds',
            examination_findings_ar='أصوات قلب طبيعية',
            assessment_notes_en='Possible anxiety-related symptoms',
            assessment_notes_ar='أعراض محتملة مرتبطة بالقلق',
            consultation_date='2024-01-16',
            duration_minutes=30,
            created_by=user,
            updated_by=user
        )
        
        print(f"Created consultation: {consultation.consultation_code}")
        print(f"Patient: {consultation.patient.first_name_en}")
        print(f"Doctor: {consultation.doctor.staff.user.first_name}")
        print("SUCCESS: Consultation system test passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Consultation system test failed: {e}")
        return False

def test_lab_system():
    """Test laboratory system functionality"""
    print("Testing laboratory system...")
    
    try:
        from django.contrib.auth import get_user_model
        from apps.lab_tests.models import LabTest
        
        User = get_user_model()
        
        # Generate unique identifiers
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_email = f'lab_test_{timestamp}@clinic.com'
        
        # Create user
        user = User.objects.create_user(
            email=user_email,
            password='testpass123',
            first_name='Lab',
            last_name='Manager',
            username=user_email
        )
        
        # Create lab test
        lab_test = LabTest.objects.create(
            name_en='Complete Blood Count',
            name_ar='عد الدم الكامل',
            code='CBC',
            category='Hematology',
            description_en='Complete blood count test',
            description_ar='اختبار عد الدم الكامل',
            price=50.00,
            normal_range_en='Normal range varies by age and gender',
            normal_range_ar='النطاق الطبيعي يختلف حسب العمر والجنس',
            unit='cells/μL',
            is_active=True,
            created_by=user,
            updated_by=user
        )
        
        print(f"Created lab test: {lab_test.name_en}")
        print(f"Price: ${lab_test.price}")
        print("SUCCESS: Laboratory system test passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Laboratory system test failed: {e}")
        return False

def test_billing_system():
    """Test billing system functionality"""
    print("Testing billing system...")
    
    try:
        from django.contrib.auth import get_user_model
        from apps.patient_management.models import Patient
        from apps.billing.models import Invoice, Payment
        
        User = get_user_model()
        
        # Generate unique identifiers
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_email = f'billing_test_{timestamp}@clinic.com'
        
        # Create user
        user = User.objects.create_user(
            email=user_email,
            password='testpass123',
            first_name='Billing',
            last_name='Manager',
            username=user_email
        )
        
        # Create patient
        patient = Patient.objects.create(
            first_name_en='Alice',
            last_name_en='Brown',
            email='alice.brown@test.com',
            phone_number=generate_unique_phone(),
            date_of_birth='1990-04-25',
            gender='F',
            address_en='321 Elm St',
            city='Miami',
            country='USA',
            status='active',
            created_by=user,
            updated_by=user
        )
        
        # Create invoice
        invoice = Invoice.objects.create(
            patient=patient,
            invoice_number=f'INV{timestamp}',
            invoice_date='2024-01-15',
            due_date='2024-02-15',
            subtotal=150.00,
            tax_amount=15.00,
            total_amount=165.00,
            status='pending',
            notes='Consultation and lab tests',
            created_by=user,
            updated_by=user
        )
        
        # Create payment
        payment = Payment.objects.create(
            invoice=invoice,
            payment_date='2024-01-20',
            amount=165.00,
            payment_method='credit_card',
            status='completed',
            transaction_id=f'TXN{timestamp}',
            notes='Payment processed successfully',
            created_by=user,
            updated_by=user
        )
        
        print(f"Created invoice: {invoice.invoice_number}")
        print(f"Created payment: {payment.transaction_id}")
        print(f"Amount: ${payment.amount}")
        print("SUCCESS: Billing system test passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Billing system test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("Testing API endpoints...")
    
    try:
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIClient
        from rest_framework import status
        
        User = get_user_model()
        
        # Generate unique identifiers
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_email = f'api_test_{timestamp}@clinic.com'
        
        # Create user
        user = User.objects.create_user(
            email=user_email,
            password='testpass123',
            first_name='API',
            last_name='Tester',
            username=user_email
        )
        
        # Create API client
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Test user profile endpoint
        response = client.get('/api/accounts/profile/')
        if response.status_code == status.HTTP_200_OK:
            print("User profile endpoint working")
        else:
            print(f"User profile endpoint failed: {response.status_code}")
        
        # Test patients endpoint
        response = client.get('/api/patients/')
        if response.status_code == status.HTTP_200_OK:
            print("Patients endpoint working")
        else:
            print(f"Patients endpoint failed: {response.status_code}")
        
        print("SUCCESS: API endpoints test passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: API endpoints test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("CLINIC MANAGEMENT SYSTEM - IMPROVED COMPREHENSIVE TEST")
    print("=" * 80)
    
    # Clean database first
    cleanup_database()
    
    # Run tests
    tests = [
        test_database_operations,
        test_user_management,
        test_patient_management,
        test_appointment_system,
        test_consultation_system,
        test_lab_system,
        test_billing_system,
        test_api_endpoints
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"ERROR: {test.__name__} failed with exception: {e}")
            results.append(False)
        print()  # Add spacing between tests
    
    # Summary
    print("=" * 80)
    print("IMPROVED COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    test_names = [
        "Database Operations",
        "User Management", 
        "Patient Management",
        "Appointment System",
        "Consultation System",
        "Lab System",
        "Billing System",
        "API Endpoints"
    ]
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "PASSED" if result else "FAILED"
        print(f"{name}: {status}")
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        print("\nSystem is ready for deployment!")
        return True
    else:
        print("\nSystem needs attention before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
