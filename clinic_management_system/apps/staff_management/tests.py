"""
Test cases for Staff Management
"""

from django.test import TestCase, Client
from apps.accounts.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, time
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import (
    Role, Specialization, Staff, Doctor, Schedule, 
    Compensation, StaffAuditLog
)


class StaffManagementTestCase(APITestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create roles
        self.admin_role = Role.objects.create(
            code='ADMIN',
            name_en='Administrator',
            name_ar='مدير',
            description_en='System administrator',
            description_ar='مدير النظام'
        )
        
        self.doctor_role = Role.objects.create(
            code='DOC',
            name_en='Doctor',
            name_ar='طبيب',
            description_en='Medical doctor',
            description_ar='طبيب'
        )
        
        self.nurse_role = Role.objects.create(
            code='NURSE',
            name_en='Nurse',
            name_ar='ممرض',
            description_en='Nursing staff',
            description_ar='طاقم التمريض'
        )
        
        # Create specializations
        self.cardiology = Specialization.objects.create(
            name_en='Cardiology',
            name_ar='أمراض القلب',
            description_en='Heart diseases',
            description_ar='أمراض القلب'
        )
        
        self.dermatology = Specialization.objects.create(
            name_en='Dermatology',
            name_ar='الأمراض الجلدية',
            description_en='Skin diseases',
            description_ar='الأمراض الجلدية'
        )
        
        # Create staff
        self.staff = Staff.objects.create(
            user=self.user,
            role=self.nurse_role,
            first_name_en='John',
            first_name_ar='جون',
            last_name_en='Doe',
            last_name_ar='دو',
            email='john.doe@example.com',
            phone_primary='+966501234567',
            address_en='123 Test Street',
            address_ar='123 شارع الاختبار',
            city='Riyadh',
            country='Saudi Arabia',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            national_id='1234567890',
            employment_status='active',
            joining_date=date(2020, 1, 1),
            created_by=self.admin_user
        )
        
        # Create doctor
        self.doctor_staff = Staff.objects.create(
            user=User.objects.create_user(
                username='doctor',
                email='doctor@example.com',
                password='doctorpass123'
            ),
            role=self.doctor_role,
            first_name_en='Dr. Jane',
            first_name_ar='د. جين',
            last_name_en='Smith',
            last_name_ar='سميث',
            email='jane.smith@example.com',
            phone_primary='+966501234568',
            address_en='456 Doctor Street',
            address_ar='456 شارع الطبيب',
            city='Jeddah',
            country='Saudi Arabia',
            gender='F',
            date_of_birth=date(1985, 5, 15),
            national_id='1234567891',
            employment_status='active',
            joining_date=date(2019, 6, 1),
            created_by=self.admin_user
        )
        
        self.doctor = Doctor.objects.create(
            staff=self.doctor_staff,
            medical_license_number='ML123456',
            professional_title_en='Dr.',
            professional_title_ar='د.',
            years_of_experience=10,
            biography_en='Experienced cardiologist',
            biography_ar='طبيب قلب ذو خبرة',
            languages=['English', 'Arabic'],
            consultation_fee=300.00,
            hourly_rate=150.00,
            is_available=True,
            is_accepting_new_patients=True
        )
        self.doctor.specializations.add(self.cardiology)
        
        # Create schedule
        self.schedule = Schedule.objects.create(
            staff=self.doctor_staff,
            day_of_week=0,  # Monday
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_active=True,
            notes='Regular working hours'
        )
        
        # Create compensation
        self.compensation = Compensation.objects.create(
            staff=self.staff,
            compensation_type='salary',
            base_salary=8000.00,
            effective_from=date(2020, 1, 1),
            notes='Monthly salary'
        )
        
        # Create tokens
        self.user_token = Token.objects.create(user=self.user)
        self.admin_token = Token.objects.create(user=self.admin_user)


class RoleAPITestCase(StaffManagementTestCase):
    """Test cases for Role API"""
    
    def test_list_roles(self):
        """Test listing roles"""
        url = reverse('staff_management:role-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_create_role_as_admin(self):
        """Test creating role as admin"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        url = reverse('staff_management:role-list')
        data = {
            'code': 'TECH',
            'name_en': 'Technician',
            'name_ar': 'فني',
            'description_en': 'Technical staff',
            'description_ar': 'طاقم تقني'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Role.objects.count(), 4)
    
    def test_create_role_as_user(self):
        """Test creating role as regular user (should fail)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('staff_management:role-list')
        data = {
            'code': 'TECH',
            'name_en': 'Technician',
            'name_ar': 'فني'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StaffAPITestCase(StaffManagementTestCase):
    """Test cases for Staff API"""
    
    def test_list_staff(self):
        """Test listing staff"""
        url = reverse('staff_management:staff-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test with authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_staff_as_admin(self):
        """Test creating staff as admin"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        url = reverse('staff_management:staff-list')
        data = {
            'username': 'newstaff',
            'password': 'newpass123',
            'role_id': self.nurse_role.id,
            'first_name_en': 'New',
            'first_name_ar': 'جديد',
            'last_name_en': 'Staff',
            'last_name_ar': 'موظف',
            'email': 'new.staff@example.com',
            'phone_primary': '+966501234569',
            'address_en': '789 New Street',
            'address_ar': '789 شارع جديد',
            'city': 'Dammam',
            'gender': 'M',
            'date_of_birth': '1992-03-15',
            'national_id': '1234567892',
            'employment_status': 'active',
            'joining_date': '2021-01-01'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Staff.objects.count(), 3)
    
    def test_staff_search(self):
        """Test staff search functionality"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('staff_management:staff-search')
        
        # Search by name
        response = self.client.get(url, {'query': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Search by role
        response = self.client.get(url, {'role': 'DOC'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_staff_stats(self):
        """Test staff statistics"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('staff_management:staff-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_staff'], 2)
        self.assertEqual(response.data['doctors'], 1)
        self.assertEqual(response.data['nurses'], 1)


class DoctorAPITestCase(StaffManagementTestCase):
    """Test cases for Doctor API"""
    
    def test_list_doctors(self):
        """Test listing doctors"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('staff_management:doctor-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_available_doctors(self):
        """Test available doctors endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('staff_management:doctor-available')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_doctor_availability_check(self):
        """Test doctor availability check"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('staff_management:doctor-availability', kwargs={'pk': self.doctor.id})
        
        # Check Monday 10 AM (should be available)
        response = self.client.get(url, {'date': '2024-01-01', 'time': '10:00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_available'])
        
        # Check Sunday 10 AM (should not be available)
        response = self.client.get(url, {'date': '2023-12-31', 'time': '10:00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_available'])


class ScheduleAPITestCase(StaffManagementTestCase):
    """Test cases for Schedule API"""
    
    def test_list_schedules(self):
        """Test listing schedules"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('staff_management:schedule-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_weekly_schedule(self):
        """Test weekly schedule endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('staff_management:schedule-weekly')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('0', response.data)  # Monday should be in the response


class ModelTestCase(TestCase):
    """Test cases for models"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.role = Role.objects.create(
            code='TEST',
            name_en='Test Role',
            name_ar='دور اختبار'
        )
        
        self.staff = Staff.objects.create(
            user=self.user,
            role=self.role,
            first_name_en='Test',
            first_name_ar='اختبار',
            last_name_en='User',
            last_name_ar='مستخدم',
            email='test@example.com',
            phone_primary='+966501234567',
            address_en='Test Address',
            address_ar='عنوان اختبار',
            city='Riyadh',
            country='Saudi Arabia',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            national_id='1234567890',
            employment_status='active',
            joining_date=date(2020, 1, 1)
        )
    
    def test_staff_str_representation(self):
        """Test staff string representation"""
        expected = f"{self.staff.first_name_en} {self.staff.last_name_en} ({self.staff.staff_id})"
        self.assertEqual(str(self.staff), expected)
    
    def test_staff_full_name_properties(self):
        """Test staff full name properties"""
        self.assertEqual(self.staff.full_name_en, "Test User")
        self.assertEqual(self.staff.full_name_ar, "اختبار مستخدم")
    
    def test_staff_id_generation(self):
        """Test automatic staff ID generation"""
        self.assertTrue(self.staff.staff_id.startswith('TES'))
        self.assertEqual(len(self.staff.staff_id), 7)  # TES + 4 digits
    
    def test_schedule_creation(self):
        """Test schedule creation"""
        schedule = Schedule.objects.create(
            staff=self.staff,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_active=True
        )
        self.assertEqual(schedule.staff, self.staff)
        self.assertEqual(schedule.day_of_week, 0)
    
    def test_schedule_validation(self):
        """Test schedule validation"""
        with self.assertRaises(Exception):  # Should raise ValidationError
            Schedule.objects.create(
                staff=self.staff,
                day_of_week=0,
                start_time=time(17, 0),  # Start after end
                end_time=time(9, 0),
                is_active=True
            )

