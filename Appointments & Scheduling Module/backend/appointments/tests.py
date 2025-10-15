"""
Tests for the appointments app.

Comprehensive test suite covering all major functionality.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, date, time, timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from .models import (
    Doctor, Patient, Appointment, DoctorAvailability, WaitingList, 
    Reminder, ClinicSettings, TimeSlot
)
from .services import AppointmentService, DoctorAvailabilityService, WaitingListService


class AppointmentModelTest(TestCase):
    """Test cases for Appointment model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.doctor_user = User.objects.create_user(
            username='doctor',
            email='doctor@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.patient_user = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            employee_id='DOC001',
            specialization={'en': 'Cardiology', 'ar': 'أمراض القلب'},
            phone='+1234567890'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            patient_id='PAT001',
            phone='+1234567891',
            date_of_birth=date(1990, 1, 1),
            gender='F'
        )
    
    def test_appointment_creation(self):
        """Test appointment creation."""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 0),
            reason_for_visit={'en': 'Regular checkup', 'ar': 'فحص دوري'},
            created_by=self.user
        )
        
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.status, 'scheduled')
        self.assertIsNotNone(appointment.appointment_code)
    
    def test_appointment_code_generation(self):
        """Test unique appointment code generation."""
        appointment1 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 0),
            reason_for_visit={'en': 'Checkup', 'ar': 'فحص'}
        )
        
        appointment2 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.today() + timedelta(days=2),
            appointment_time=time(11, 0),
            reason_for_visit={'en': 'Follow-up', 'ar': 'متابعة'}
        )
        
        self.assertNotEqual(appointment1.appointment_code, appointment2.appointment_code)
        self.assertTrue(appointment1.appointment_code.startswith('APT'))
        self.assertTrue(appointment2.appointment_code.startswith('APT'))


class DoctorAvailabilityTest(TestCase):
    """Test cases for DoctorAvailability model."""
    
    def setUp(self):
        """Set up test data."""
        self.doctor_user = User.objects.create_user(
            username='doctor',
            email='doctor@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            employee_id='DOC001',
            specialization={'en': 'Cardiology', 'ar': 'أمراض القلب'},
            phone='+1234567890'
        )
    
    def test_availability_creation(self):
        """Test doctor availability creation."""
        availability = DoctorAvailability.objects.create(
            doctor=self.doctor,
            day_of_week=0,  # Monday
            start_time=time(9, 0),
            end_time=time(17, 0),
            time_slot_duration=30
        )
        
        self.assertEqual(availability.doctor, self.doctor)
        self.assertEqual(availability.day_of_week, 0)
        self.assertEqual(availability.start_time, time(9, 0))
        self.assertEqual(availability.end_time, time(17, 0))


class AppointmentServiceTest(TestCase):
    """Test cases for AppointmentService."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.doctor_user = User.objects.create_user(
            username='doctor',
            email='doctor@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.patient_user = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            employee_id='DOC001',
            specialization={'en': 'Cardiology', 'ar': 'أمراض القلب'},
            phone='+1234567890'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            patient_id='PAT001',
            phone='+1234567891',
            date_of_birth=date(1990, 1, 1),
            gender='F'
        )
        
        # Create doctor availability
        DoctorAvailability.objects.create(
            doctor=self.doctor,
            day_of_week=0,  # Monday
            start_time=time(9, 0),
            end_time=time(17, 0),
            time_slot_duration=30
        )
    
    def test_is_doctor_available(self):
        """Test doctor availability checking."""
        tomorrow = date.today() + timedelta(days=1)
        monday = tomorrow + timedelta(days=(7 - tomorrow.weekday()) % 7)
        
        # Test available time
        is_available = AppointmentService.is_doctor_available(
            str(self.doctor.id), monday, time(10, 0)
        )
        self.assertTrue(is_available)
        
        # Test unavailable time (outside working hours)
        is_available = AppointmentService.is_doctor_available(
            str(self.doctor.id), monday, time(18, 0)
        )
        self.assertFalse(is_available)
    
    def test_create_appointment(self):
        """Test appointment creation through service."""
        tomorrow = date.today() + timedelta(days=1)
        monday = tomorrow + timedelta(days=(7 - tomorrow.weekday()) % 7)
        
        appointment = AppointmentService.create_appointment(
            patient_id=str(self.patient.id),
            doctor_id=str(self.doctor.id),
            appointment_date=monday,
            appointment_time=time(10, 0),
            reason_for_visit={'en': 'Checkup', 'ar': 'فحص'},
            created_by=self.user
        )
        
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.status, 'scheduled')


class AppointmentAPITest(APITestCase):
    """Test cases for Appointment API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.doctor_user = User.objects.create_user(
            username='doctor',
            email='doctor@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.patient_user = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            employee_id='DOC001',
            specialization={'en': 'Cardiology', 'ar': 'أمراض القلب'},
            phone='+1234567890'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            patient_id='PAT001',
            phone='+1234567891',
            date_of_birth=date(1990, 1, 1),
            gender='F'
        )
        
        # Create doctor availability
        DoctorAvailability.objects.create(
            doctor=self.doctor,
            day_of_week=0,  # Monday
            start_time=time(9, 0),
            end_time=time(17, 0),
            time_slot_duration=30
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_create_appointment_api(self):
        """Test appointment creation via API."""
        tomorrow = date.today() + timedelta(days=1)
        monday = tomorrow + timedelta(days=(7 - tomorrow.weekday()) % 7)
        
        data = {
            'patient_id': str(self.patient.id),
            'doctor_id': str(self.doctor.id),
            'appointment_date': monday.isoformat(),
            'appointment_time': '10:00:00',
            'reason_for_visit': {'en': 'Checkup', 'ar': 'فحص'},
            'duration_minutes': 30
        }
        
        response = self.client.post('/api/appointments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('appointment_code', response.data)
    
    def test_get_appointments_api(self):
        """Test getting appointments via API."""
        # Create an appointment
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 0),
            reason_for_visit={'en': 'Checkup', 'ar': 'فحص'},
            created_by=self.user
        )
        
        response = self.client.get('/api/appointments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search_appointments_api(self):
        """Test appointment search via API."""
        # Create an appointment
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=time(10, 0),
            reason_for_visit={'en': 'Checkup', 'ar': 'فحص'},
            created_by=self.user
        )
        
        response = self.client.get('/api/appointments/search/?patient_name=Jane')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_appointment_statistics_api(self):
        """Test appointment statistics via API."""
        response = self.client.get('/api/appointments/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_appointments', response.data)


class WaitingListTest(TestCase):
    """Test cases for WaitingList functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.doctor_user = User.objects.create_user(
            username='doctor',
            email='doctor@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.patient_user = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            employee_id='DOC001',
            specialization={'en': 'Cardiology', 'ar': 'أمراض القلب'},
            phone='+1234567890'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            patient_id='PAT001',
            phone='+1234567891',
            date_of_birth=date(1990, 1, 1),
            gender='F'
        )
    
    def test_add_to_waiting_list(self):
        """Test adding patient to waiting list."""
        waiting_entry = WaitingListService.add_to_waiting_list(
            patient_id=str(self.patient.id),
            doctor_id=str(self.doctor.id),
            preferred_date=date.today() + timedelta(days=1),
            preferred_time_start=time(10, 0),
            preferred_time_end=time(11, 0),
            reason_for_visit={'en': 'Urgent consultation', 'ar': 'استشارة عاجلة'},
            priority=1
        )
        
        self.assertEqual(waiting_entry.patient, self.patient)
        self.assertEqual(waiting_entry.doctor, self.doctor)
        self.assertEqual(waiting_entry.priority, 1)
        self.assertEqual(waiting_entry.status, 'waiting')
