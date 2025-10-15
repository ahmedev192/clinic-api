"""
Comprehensive tests for Patient Management module.
"""

from django.test import TestCase
from apps.accounts.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from django.utils import timezone

from .models import (
    Patient, MedicalHistory, Allergy, ChronicCondition, 
    PatientDocument, PatientSearchLog
)
from .utils import (
    generate_patient_code, validate_national_id, validate_phone_number,
    calculate_age, format_patient_name, get_patient_statistics
)


class PatientModelTests(TestCase):
    """Test cases for Patient model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.patient_data = {
            'first_name_en': 'Ahmed',
            'first_name_ar': 'أحمد',
            'last_name_en': 'Al-Rashid',
            'last_name_ar': 'الرشيد',
            'gender': 'M',
            'date_of_birth': date(1990, 1, 1),
            'phone_number': '+966501234567',
            'email': 'ahmed@example.com',
            'address_en': '123 Main Street, Riyadh',
            'address_ar': 'شارع الرئيسي 123، الرياض',
            'city': 'Riyadh',
            'state_province': 'Riyadh Province',
            'postal_code': '12345',
            'country': 'Saudi Arabia',
            'national_id': '1234567890',
            'blood_type': 'A+',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '+966501234568',
            'emergency_contact_relationship': 'Brother',
            'notes': 'Test patient',
            'created_by': self.user,
            'updated_by': self.user
        }
    
    def test_patient_creation(self):
        """Test patient creation"""
        patient = Patient.objects.create(**self.patient_data)
        
        self.assertEqual(patient.first_name_en, 'Ahmed')
        self.assertEqual(patient.first_name_ar, 'أحمد')
        self.assertEqual(patient.get_full_name(), 'Ahmed Al-Rashid')
        self.assertEqual(patient.get_full_name_ar(), 'أحمد الرشيد')
        self.assertTrue(patient.patient_code.startswith('PAT-'))
        self.assertFalse(patient.is_deleted)
    
    def test_patient_code_generation(self):
        """Test patient code generation"""
        patient1 = Patient.objects.create(**self.patient_data)
        patient2 = Patient.objects.create(**self.patient_data)
        
        self.assertNotEqual(patient1.patient_code, patient2.patient_code)
        self.assertTrue(patient1.patient_code.startswith('PAT-'))
        self.assertTrue(patient2.patient_code.startswith('PAT-'))
    
    def test_patient_age_calculation(self):
        """Test age calculation"""
        patient = Patient.objects.create(**self.patient_data)
        expected_age = 34  # As of 2024
        self.assertEqual(patient.get_age(), expected_age)
    
    def test_soft_delete(self):
        """Test soft delete functionality"""
        patient = Patient.objects.create(**self.patient_data)
        
        patient.soft_delete(self.user)
        
        self.assertTrue(patient.is_deleted)
        self.assertIsNotNone(patient.deleted_at)
        self.assertEqual(patient.deleted_by, self.user)
        self.assertEqual(patient.status, 'archived')
    
    def test_patient_str_representation(self):
        """Test string representation"""
        patient = Patient.objects.create(**self.patient_data)
        expected = f"{patient.patient_code} - {patient.get_full_name()}"
        self.assertEqual(str(patient), expected)


class MedicalHistoryModelTests(TestCase):
    """Test cases for MedicalHistory model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.patient = Patient.objects.create(
            first_name_en='Ahmed',
            last_name_en='Al-Rashid',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            phone_number='+966501234567',
            national_id='1234567890',
            created_by=self.user,
            updated_by=self.user
        )
    
    def test_medical_history_creation(self):
        """Test medical history creation"""
        history = MedicalHistory.objects.create(
            patient=self.patient,
            category='diagnosis',
            title_en='Diabetes Diagnosis',
            title_ar='تشخيص السكري',
            description_en='Patient diagnosed with Type 2 diabetes',
            description_ar='تم تشخيص المريض بمرض السكري من النوع الثاني',
            event_date=date(2020, 1, 1),
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(history.patient, self.patient)
        self.assertEqual(history.category, 'diagnosis')
        self.assertEqual(history.title_en, 'Diabetes Diagnosis')
        self.assertEqual(history.title_ar, 'تشخيص السكري')


class AllergyModelTests(TestCase):
    """Test cases for Allergy model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.patient = Patient.objects.create(
            first_name_en='Ahmed',
            last_name_en='Al-Rashid',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            phone_number='+966501234567',
            national_id='1234567890',
            created_by=self.user,
            updated_by=self.user
        )
    
    def test_allergy_creation(self):
        """Test allergy creation"""
        allergy = Allergy.objects.create(
            patient=self.patient,
            allergy_type='medication',
            allergen_en='Penicillin',
            allergen_ar='البنسلين',
            description_en='Allergic to penicillin',
            description_ar='حساسية من البنسلين',
            severity='severe',
            symptoms='Rash, difficulty breathing',
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(allergy.patient, self.patient)
        self.assertEqual(allergy.allergy_type, 'medication')
        self.assertEqual(allergy.allergen_en, 'Penicillin')
        self.assertEqual(allergy.allergen_ar, 'البنسلين')
        self.assertEqual(allergy.severity, 'severe')


class ChronicConditionModelTests(TestCase):
    """Test cases for ChronicCondition model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.patient = Patient.objects.create(
            first_name_en='Ahmed',
            last_name_en='Al-Rashid',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            phone_number='+966501234567',
            national_id='1234567890',
            created_by=self.user,
            updated_by=self.user
        )
    
    def test_chronic_condition_creation(self):
        """Test chronic condition creation"""
        condition = ChronicCondition.objects.create(
            patient=self.patient,
            condition_type='diabetes',
            condition_name_en='Type 2 Diabetes',
            condition_name_ar='السكري من النوع الثاني',
            description_en='Chronic diabetes condition',
            description_ar='حالة مزمنة من السكري',
            severity='moderate',
            diagnosis_date=date(2020, 1, 1),
            is_active=True,
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(condition.patient, self.patient)
        self.assertEqual(condition.condition_type, 'diabetes')
        self.assertEqual(condition.condition_name_en, 'Type 2 Diabetes')
        self.assertEqual(condition.condition_name_ar, 'السكري من النوع الثاني')
        self.assertTrue(condition.is_active)


class PatientDocumentModelTests(TestCase):
    """Test cases for PatientDocument model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.patient = Patient.objects.create(
            first_name_en='Ahmed',
            last_name_en='Al-Rashid',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            phone_number='+966501234567',
            national_id='1234567890',
            created_by=self.user,
            updated_by=self.user
        )
    
    def test_document_creation(self):
        """Test document creation"""
        # Create a simple file for testing
        file_content = b'Test document content'
        uploaded_file = SimpleUploadedFile(
            'test_document.pdf',
            file_content,
            content_type='application/pdf'
        )
        
        document = PatientDocument.objects.create(
            patient=self.patient,
            document_type='medical_report',
            title_en='Test Medical Report',
            title_ar='تقرير طبي تجريبي',
            file=uploaded_file,
            uploaded_by=self.user
        )
        
        self.assertEqual(document.patient, self.patient)
        self.assertEqual(document.document_type, 'medical_report')
        self.assertEqual(document.title_en, 'Test Medical Report')
        self.assertEqual(document.title_ar, 'تقرير طبي تجريبي')
        self.assertEqual(document.file_size, len(file_content))
        self.assertEqual(document.file_extension, '.pdf')


class UtilsTests(TestCase):
    """Test cases for utility functions"""
    
    def test_validate_national_id(self):
        """Test national ID validation"""
        # Valid national ID
        valid_id = '1234567890'
        self.assertEqual(validate_national_id(valid_id), valid_id)
        
        # Invalid national ID (too short)
        with self.assertRaises(Exception):
            validate_national_id('123456789')
        
        # Invalid national ID (too long)
        with self.assertRaises(Exception):
            validate_national_id('12345678901')
    
    def test_validate_phone_number(self):
        """Test phone number validation"""
        # Valid phone number
        valid_phone = '+966501234567'
        self.assertEqual(validate_phone_number(valid_phone), valid_phone)
    
    def test_calculate_age(self):
        """Test age calculation"""
        birth_date = date(1990, 1, 1)
        expected_age = 34  # As of 2024
        self.assertEqual(calculate_age(birth_date), expected_age)
    
    def test_format_patient_name(self):
        """Test patient name formatting"""
        # English name
        english_name = format_patient_name(
            'Ahmed', 'Al-Rashid', 'Mohammed',
            language='en'
        )
        self.assertEqual(english_name, 'Ahmed Mohammed Al-Rashid')
        
        # Arabic name
        arabic_name = format_patient_name(
            'Ahmed', 'Al-Rashid', 'Mohammed',
            'أحمد', 'الرشيد', 'محمد',
            language='ar'
        )
        self.assertEqual(arabic_name, 'أحمد محمد الرشيد')
    
    def test_get_patient_statistics(self):
        """Test patient statistics"""
        # Create test data
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        Patient.objects.create(
            first_name_en='Ahmed',
            last_name_en='Al-Rashid',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            phone_number='+966501234567',
            national_id='1234567890',
            created_by=user,
            updated_by=user
        )
        
        stats = get_patient_statistics()
        self.assertIn('total_patients', stats)
        self.assertIn('active_patients', stats)
        self.assertIn('patients_this_month', stats)


class PatientAPITests(APITestCase):
    """Test cases for Patient API"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create groups
        self.doctor_group = Group.objects.create(name='doctors')
        self.nurse_group = Group.objects.create(name='nurses')
        self.receptionist_group = Group.objects.create(name='receptionists')
        self.admin_group = Group.objects.create(name='administrators')
        
        self.user.groups.add(self.doctor_group)
        
        self.patient_data = {
            'first_name_en': 'Ahmed',
            'first_name_ar': 'أحمد',
            'last_name_en': 'Al-Rashid',
            'last_name_ar': 'الرشيد',
            'gender': 'M',
            'date_of_birth': '1990-01-01',
            'phone_number': '+966501234567',
            'email': 'ahmed@example.com',
            'address_en': '123 Main Street, Riyadh',
            'address_ar': 'شارع الرئيسي 123، الرياض',
            'city': 'Riyadh',
            'state_province': 'Riyadh Province',
            'postal_code': '12345',
            'country': 'Saudi Arabia',
            'national_id': '1234567890',
            'blood_type': 'A+',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '+966501234568',
            'emergency_contact_relationship': 'Brother',
            'notes': 'Test patient'
        }
    
    def test_create_patient(self):
        """Test patient creation via API"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/v1/patients/patients/', self.patient_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 1)
        
        patient = Patient.objects.first()
        self.assertEqual(patient.first_name_en, 'Ahmed')
        self.assertEqual(patient.first_name_ar, 'أحمد')
        self.assertEqual(patient.created_by, self.user)
    
    def test_list_patients(self):
        """Test patient listing via API"""
        # Create a patient
        patient = Patient.objects.create(
            first_name_en='Ahmed',
            last_name_en='Al-Rashid',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            phone_number='+966501234567',
            national_id='1234567890',
            created_by=self.user,
            updated_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/patients/patients/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name_en'], 'Ahmed')
    
    def test_patient_search(self):
        """Test patient search functionality"""
        # Create a patient
        patient = Patient.objects.create(
            first_name_en='Ahmed',
            last_name_en='Al-Rashid',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            phone_number='+966501234567',
            national_id='1234567890',
            created_by=self.user,
            updated_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        
        # Search by name
        response = self.client.get('/api/v1/patients/patients/search/?q=Ahmed')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name_en'], 'Ahmed')
    
    def test_patient_statistics(self):
        """Test patient statistics endpoint"""
        # Create a patient
        Patient.objects.create(
            first_name_en='Ahmed',
            last_name_en='Al-Rashid',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            phone_number='+966501234567',
            national_id='1234567890',
            created_by=self.user,
            updated_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/patients/patients/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_patients', response.data)
        self.assertEqual(response.data['total_patients'], 1)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to patient data"""
        response = self.client.get('/api/v1/patients/patients/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_patient_export(self):
        """Test patient export functionality"""
        # Create a patient
        Patient.objects.create(
            first_name_en='Ahmed',
            last_name_en='Al-Rashid',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            phone_number='+966501234567',
            national_id='1234567890',
            created_by=self.user,
            updated_by=self.user
        )
        
        self.user.groups.add(self.receptionist_group)  # Add export permission
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/patients/patients/export/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('Patient Code', response.content.decode())


class MedicalHistoryAPITests(APITestCase):
    """Test cases for MedicalHistory API"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.doctor_group = Group.objects.create(name='doctors')
        self.user.groups.add(self.doctor_group)
        
        self.patient = Patient.objects.create(
            first_name_en='Ahmed',
            last_name_en='Al-Rashid',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            phone_number='+966501234567',
            national_id='1234567890',
            created_by=self.user,
            updated_by=self.user
        )
    
    def test_create_medical_history(self):
        """Test medical history creation via API"""
        self.client.force_authenticate(user=self.user)
        
        history_data = {
            'patient': self.patient.id,
            'category': 'diagnosis',
            'title_en': 'Diabetes Diagnosis',
            'title_ar': 'تشخيص السكري',
            'description_en': 'Patient diagnosed with Type 2 diabetes',
            'description_ar': 'تم تشخيص المريض بمرض السكري من النوع الثاني',
            'event_date': '2020-01-01'
        }
        
        response = self.client.post('/api/v1/patients/medical-history/', history_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicalHistory.objects.count(), 1)
        
        history = MedicalHistory.objects.first()
        self.assertEqual(history.patient, self.patient)
        self.assertEqual(history.title_en, 'Diabetes Diagnosis')
        self.assertEqual(history.created_by, self.user)


class AllergyAPITests(APITestCase):
    """Test cases for Allergy API"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.doctor_group = Group.objects.create(name='doctors')
        self.user.groups.add(self.doctor_group)
        
        self.patient = Patient.objects.create(
            first_name_en='Ahmed',
            last_name_en='Al-Rashid',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            phone_number='+966501234567',
            national_id='1234567890',
            created_by=self.user,
            updated_by=self.user
        )
    
    def test_create_allergy(self):
        """Test allergy creation via API"""
        self.client.force_authenticate(user=self.user)
        
        allergy_data = {
            'patient': self.patient.id,
            'allergy_type': 'medication',
            'allergen_en': 'Penicillin',
            'allergen_ar': 'البنسلين',
            'description_en': 'Allergic to penicillin',
            'description_ar': 'حساسية من البنسلين',
            'severity': 'severe',
            'symptoms': 'Rash, difficulty breathing'
        }
        
        response = self.client.post('/api/v1/patients/allergies/', allergy_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Allergy.objects.count(), 1)
        
        allergy = Allergy.objects.first()
        self.assertEqual(allergy.patient, self.patient)
        self.assertEqual(allergy.allergen_en, 'Penicillin')
        self.assertEqual(allergy.created_by, self.user)

