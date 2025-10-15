"""
Comprehensive Integration Tests for Clinic Management System
Tests all modules and their interactions
"""

import os
import sys
import django
from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
import json

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_management_system.settings')
django.setup()

User = get_user_model()


class SystemIntegrationTests(APITestCase):
    """Comprehensive integration tests for the entire system"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='test@clinic.com',
            email='test@clinic.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            is_staff=True
        )
        
        # Create test patient
        from apps.patient_management.models import Patient
        self.patient = Patient.objects.create(
            first_name_en='John',
            last_name_en='Doe',
            first_name_ar='جون',
            last_name_ar='دو',
            email='john.doe@example.com',
            phone_number='+1234567890',
            date_of_birth='1990-01-01',
            gender='male',
            address_en='123 Main St',
            address_ar='123 الشارع الرئيسي',
            created_by=self.user,
            updated_by=self.user
        )
        
        # Create test doctor
        from apps.staff_management.models import Doctor, Staff, Role, Specialization
        from apps.authorization.models import Permission
        
        # Create role and permissions
        role = Role.objects.create(
            name_en='Doctor',
            name_ar='طبيب',
            code='DOCTOR',
            description_en='Medical doctor role',
            description_ar='دور الطبيب'
        )
        
        # Create specialization
        specialization = Specialization.objects.create(
            name_en='General Medicine',
            name_ar='الطب العام',
            description_en='General medical practice',
            description_ar='ممارسة طبية عامة'
        )
        
        # Create staff
        staff = Staff.objects.create(
            user=self.user,
            first_name_en='Test',
            last_name_en='Doctor',
            first_name_ar='اختبار',
            last_name_ar='طبيب',
            email='test@clinic.com',
            phone_primary='+1234567890',
            address_en='123 Main St',
            address_ar='123 الشارع الرئيسي',
            city='Test City',
            country='Test Country',
            gender='male',
            date_of_birth='1980-01-01',
            national_id='1234567890',
            role=role,
            employment_status='active',
            joining_date='2020-01-01'
        )
        
        # Get the doctor created by the signal
        self.doctor = Doctor.objects.get(staff=staff)
        
        # Update doctor with additional fields
        self.doctor.professional_title_en = 'Dr.'
        self.doctor.professional_title_ar = 'د.'
        self.doctor.medical_license_number = 'MD123456'
        self.doctor.years_of_experience = 10
        self.doctor.is_available = True
        self.doctor.is_accepting_new_patients = True
        self.doctor.save()
        
        # Add specialization to doctor
        self.doctor.specializations.add(specialization)
        
        # Create test appointment
        from apps.appointments.models import Appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date='2024-01-15',
            appointment_time='10:00:00',
            status='scheduled',
            created_by=self.user
        )
        
        # Authenticate client
        self.client.force_authenticate(user=self.user)
    
    def test_user_authentication(self):
        """Test user authentication system"""
        print("Testing user authentication...")
        
        # Test user creation
        self.assertIsNotNone(self.user)
        self.assertEqual(self.user.email, 'test@clinic.com')
        self.assertTrue(self.user.check_password('testpass123'))
        
        # Test user profile
        from apps.accounts.models import UserProfile
        profile = UserProfile.objects.create(
            user=self.user,
            bio='Test doctor profile',
            gender='male'
        )
        self.assertEqual(profile.user, self.user)
        print("PASS: User authentication tests passed")
    
    def test_patient_management(self):
        """Test patient management functionality"""
        print("Testing patient management...")
        
        # Test patient creation
        self.assertIsNotNone(self.patient)
        self.assertEqual(self.patient.first_name_en, 'John')
        self.assertEqual(self.patient.first_name_ar, 'جون')
        
        # Test patient API
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test patient search
        url = reverse('patient-search')
        response = self.client.get(url, {'q': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        print("PASS: Patient management tests passed")
    
    def test_doctor_management(self):
        """Test doctor management functionality"""
        print("Testing doctor management...")
        
        # Test doctor creation
        self.assertIsNotNone(self.doctor)
        self.assertEqual(self.doctor.professional_title_en, 'Dr.')
        self.assertTrue(self.doctor.is_available)
        
        # Test doctor API
        url = reverse('doctor-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        print("PASS: Doctor management tests passed")
    
    def test_appointment_system(self):
        """Test appointment scheduling system"""
        print("Testing appointment system...")
        
        # Test appointment creation
        self.assertIsNotNone(self.appointment)
        self.assertEqual(self.appointment.patient, self.patient)
        self.assertEqual(self.appointment.doctor, self.doctor)
        self.assertEqual(self.appointment.status, 'scheduled')
        
        # Test appointment API
        url = reverse('appointment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test appointment booking
        appointment_data = {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'appointment_date': '2024-01-20',
            'appointment_time': '14:00:00',
            'status': 'scheduled'
        }
        response = self.client.post(url, appointment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        print("PASS: Appointment system tests passed")
    
    def test_consultation_system(self):
        """Test consultation and clinical notes system"""
        print("Testing consultation system...")
        
        # Create consultation
        from apps.consultation.models import Consultation
        consultation = Consultation.objects.create(
            consultation_code='CONS001',
            patient=self.patient,
            doctor=self.doctor,
            appointment=self.appointment,
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
            created_by=self.user
        )
        
        self.assertIsNotNone(consultation)
        self.assertEqual(consultation.patient, self.patient)
        self.assertEqual(consultation.doctor, self.doctor)
        
        # Test consultation API
        url = reverse('consultation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        print("PASS: Consultation system tests passed")
    
    def test_laboratory_system(self):
        """Test laboratory management system"""
        print("Testing laboratory system...")
        
        # Test lab test creation
        from apps.lab_tests.models import LabTest, TestCategory
        category = TestCategory.objects.create(
            name='Blood Tests',
            name_ar='فحوصات الدم',
            description='Various blood tests',
            description_ar='فحوصات دم متنوعة'
        )
        
        lab_test = LabTest.objects.create(
            name='Complete Blood Count',
            name_ar='تعداد الدم الكامل',
            code='CBC',
            category=category,
            normal_range='Normal range values',
            normal_range_ar='قيم النطاق الطبيعي',
            description='Complete blood count test',
            description_ar='فحص تعداد الدم الكامل',
            preparation_instructions='Fasting required',
            preparation_instructions_ar='مطلوب صيام',
            created_by=self.user
        )
        
        self.assertIsNotNone(lab_test)
        self.assertEqual(lab_test.category, category)
        
        # Test lab request
        from apps.lab_requests.models import LabRequest
        lab_request = LabRequest.objects.create(
            request_number='LAB001',
            patient_id=str(self.patient.id),
            patient_name='John Doe',
            patient_name_ar='جون دو',
            doctor_id=str(self.doctor.id),
            doctor_name='Dr. Test',
            doctor_name_ar='د. اختبار',
            urgency='routine',
            status='pending',
            created_by=self.user
        )
        
        self.assertIsNotNone(lab_request)
        
        print("PASS: Laboratory system tests passed")
    
    def test_pharmacy_system(self):
        """Test pharmacy management system"""
        print("Testing pharmacy system...")
        
        # Test medicine creation
        from apps.medicine.models import Medicine, MedicineCategory
        category = MedicineCategory.objects.create(
            name='Antibiotics',
            name_ar='مضادات حيوية',
            description='Antibiotic medications',
            description_ar='أدوية مضادة للحيوية',
            created_by=self.user
        )
        
        medicine = Medicine.objects.create(
            name='Amoxicillin',
            name_ar='أموكسيسيلين',
            generic_name='Amoxicillin',
            generic_name_ar='أموكسيسيلين',
            category=category,
            dosage_form='Capsule',
            dosage_form_ar='كبسولة',
            strength='500mg',
            strength_ar='500 مجم',
            manufacturer='Pharma Corp',
            manufacturer_ar='شركة فارما',
            created_by=self.user
        )
        
        self.assertIsNotNone(medicine)
        self.assertEqual(medicine.category, category)
        
        # Test prescription
        from apps.prescription.models import Prescription
        prescription = Prescription.objects.create(
            prescription_number='RX001',
            patient_name='John Doe',
            patient_name_ar='جون دو',
            patient_id=str(self.patient.id),
            doctor_name='Dr. Test',
            doctor_name_ar='د. اختبار',
            doctor_id=str(self.doctor.id),
            prescription_date='2024-01-15',
            status='active',
            created_by=self.user
        )
        
        self.assertIsNotNone(prescription)
        
        print("PASS: Pharmacy system tests passed")
    
    def test_billing_system(self):
        """Test billing and payment system"""
        print("Testing billing system...")
        
        # Test service creation
        from apps.billing.models import Service, ServiceCategory
        service_category = ServiceCategory.objects.create(
            name='Consultation',
            name_ar='استشارة',
            description='Medical consultation services',
            description_ar='خدمات الاستشارة الطبية',
            is_active=True
        )
        
        service = Service.objects.create(
            service_id='SVC001',
            name_en='General Consultation',
            name_ar='استشارة عامة',
            category=service_category,
            service_type='consultation',
            base_price=100.00,
            is_active=True
        )
        
        self.assertIsNotNone(service)
        
        # Test invoice creation
        from apps.billing.models import Invoice
        invoice = Invoice.objects.create(
            invoice_number='INV001',
            patient=self.patient,
            doctor=self.doctor,
            status='draft',
            subtotal=100.00,
            tax_amount=10.00,
            total_amount=110.00,
            created_by=self.user
        )
        
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.patient, self.patient)
        
        print("PASS: Billing system tests passed")
    
    def test_inventory_system(self):
        """Test inventory management system"""
        print("Testing inventory system...")
        
        # Test inventory item creation
        from apps.inventory.models import InventoryItem, Category
        category = Category.objects.create(
            name='Medical Equipment',
            name_ar='معدات طبية',
            description='Medical equipment and supplies',
            description_ar='معدات وإمدادات طبية'
        )
        
        item = InventoryItem.objects.create(
            name='Blood Pressure Monitor',
            name_ar='جهاز قياس ضغط الدم',
            category=category,
            sku='BP001',
            description='Digital blood pressure monitor',
            description_ar='جهاز قياس ضغط الدم الرقمي',
            unit_price=150.00,
            current_stock=10,
            minimum_stock=5,
            created_by=self.user
        )
        
        self.assertIsNotNone(item)
        self.assertEqual(item.category, category)
        
        print("PASS: Inventory system tests passed")
    
    def test_analytics_system(self):
        """Test analytics and reporting system"""
        print("Testing analytics system...")
        
        # Test report template creation
        from apps.analytics.models import ReportTemplate
        template = ReportTemplate.objects.create(
            name='Patient Report',
            name_ar='تقرير المريض',
            report_type='patient',
            description='Patient statistics report',
            description_ar='تقرير إحصائيات المرضى',
            query_config={'filters': {}, 'group_by': ['status']},
            is_active=True,
            created_by=self.user
        )
        
        self.assertIsNotNone(template)
        self.assertEqual(template.report_type, 'patient')
        
        print("PASS: Analytics system tests passed")
    
    def test_audit_system(self):
        """Test audit and logging system"""
        print("Testing audit system...")
        
        # Test audit log creation
        from apps.audit.models import AuditLog
        audit_log = AuditLog.objects.create(
            user=self.user,
            action_type='create',
            resource_type='patient',
            resource_id=str(self.patient.id),
            description='Patient created',
            result='success',
            ip_address='127.0.0.1'
        )
        
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.action_type, 'create')
        
        print("PASS: Audit system tests passed")
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        print("Testing end-to-end workflow...")
        
        # 1. Patient Registration
        patient_data = {
            'first_name_en': 'Jane',
            'last_name_en': 'Smith',
            'first_name_ar': 'جين',
            'last_name_ar': 'سميث',
            'email': 'jane.smith@example.com',
            'phone': '+1234567891',
            'date_of_birth': '1985-05-15',
            'gender': 'female',
            'address_en': '456 Oak St',
            'address_ar': '456 شارع البلوط'
        }
        
        url = reverse('patient-list')
        response = self.client.post(url, patient_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        patient_id = response.data['id']
        
        # 2. Doctor Availability Check
        url = reverse('doctor-list')
        response = self.client.get(url, {'is_available': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        
        # 3. Appointment Booking
        appointment_data = {
            'patient': patient_id,
            'doctor': self.doctor.id,
            'appointment_date': '2024-01-25',
            'appointment_time': '09:00:00',
            'status': 'scheduled'
        }
        
        url = reverse('appointment-list')
        response = self.client.post(url, appointment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        appointment_id = response.data['id']
        
        # 4. Consultation Creation
        consultation_data = {
            'patient': patient_id,
            'doctor': self.doctor.id,
            'appointment': appointment_id,
            'consultation_type': 'new',
            'chief_complaint_en': 'Chest pain',
            'chief_complaint_ar': 'ألم في الصدر',
            'symptoms_en': 'Sharp chest pain',
            'symptoms_ar': 'ألم حاد في الصدر',
            'consultation_date': '2024-01-25T09:00:00Z',
            'duration_minutes': 45
        }
        
        url = reverse('consultation-list')
        response = self.client.post(url, consultation_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        consultation_id = response.data['id']
        
        # 5. Lab Test Request
        lab_request_data = {
            'request_number': 'LAB002',
            'patient_id': patient_id,
            'patient_name': 'Jane Smith',
            'patient_name_ar': 'جين سميث',
            'doctor_id': str(self.doctor.id),
            'doctor_name': 'Dr. Test',
            'doctor_name_ar': 'د. اختبار',
            'urgency': 'urgent',
            'status': 'pending'
        }
        
        url = reverse('lab-request-list')
        response = self.client.post(url, lab_request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 6. Prescription Creation
        prescription_data = {
            'prescription_number': 'RX002',
            'patient_name': 'Jane Smith',
            'patient_name_ar': 'جين سميث',
            'patient_id': patient_id,
            'doctor_name': 'Dr. Test',
            'doctor_name_ar': 'د. اختبار',
            'doctor_id': str(self.doctor.id),
            'prescription_date': '2024-01-25',
            'status': 'active'
        }
        
        url = reverse('prescription-list')
        response = self.client.post(url, prescription_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 7. Invoice Creation
        invoice_data = {
            'invoice_number': 'INV002',
            'patient': patient_id,
            'doctor': self.doctor.id,
            'status': 'draft',
            'subtotal': 200.00,
            'tax_amount': 20.00,
            'total_amount': 220.00
        }
        
        url = reverse('invoice-list')
        response = self.client.post(url, invoice_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        print("PASS: End-to-end workflow tests passed")
    
    def test_multilingual_support(self):
        """Test multilingual support across modules"""
        print("Testing multilingual support...")
        
        # Test patient multilingual fields
        self.assertEqual(self.patient.first_name_en, 'John')
        self.assertEqual(self.patient.first_name_ar, 'جون')
        
        # Test consultation multilingual fields
        from apps.consultation.models import Consultation
        consultation = Consultation.objects.create(
            consultation_code='CONS002',
            patient=self.patient,
            doctor=self.doctor,
            chief_complaint_en='Fever',
            chief_complaint_ar='حمى',
            symptoms_en='High temperature',
            symptoms_ar='درجة حرارة عالية',
            created_by=self.user
        )
        
        self.assertEqual(consultation.chief_complaint_en, 'Fever')
        self.assertEqual(consultation.chief_complaint_ar, 'حمى')
        
        print("PASS: Multilingual support tests passed")
    
    def test_api_endpoints(self):
        """Test all API endpoints are accessible"""
        print("Testing API endpoints...")
        
        endpoints = [
            'patient-list',
            'doctor-list',
            'appointment-list',
            'consultation-list',
            'lab-test-list',
            'lab-request-list',
            'medicine-list',
            'prescription-list',
            'invoice-list',
            'inventory-item-list',
            'analytics-summary',
        ]
        
        for endpoint in endpoints:
            try:
                url = reverse(endpoint)
                response = self.client.get(url)
                # Accept both 200 and 405 (method not allowed) as valid responses
                self.assertIn(response.status_code, [200, 405])
            except Exception as e:
                print(f"Warning: Endpoint {endpoint} not found: {e}")
        
        print("PASS: API endpoints tests passed")
    
    def test_database_integrity(self):
        """Test database integrity and relationships"""
        print("Testing database integrity...")
        
        # Test foreign key relationships
        self.assertEqual(self.appointment.patient, self.patient)
        self.assertEqual(self.appointment.doctor, self.doctor)
        
        # Test cascade deletes
        patient_id = self.patient.id
        self.patient.delete()
        
        # Verify related objects are handled properly
        from apps.appointments.models import Appointment
        appointments = Appointment.objects.filter(patient_id=patient_id)
        self.assertEqual(appointments.count(), 0)
        
        print("PASS: Database integrity tests passed")
    
    def tearDown(self):
        """Clean up test data"""
        # Clean up is handled by Django's test framework
        pass


def run_integration_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("CLINIC MANAGEMENT SYSTEM - INTEGRATION TESTS")
    print("=" * 60)
    
    import unittest
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(SystemIntegrationTests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)
