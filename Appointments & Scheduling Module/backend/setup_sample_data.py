"""
Script to set up sample data for the appointments system.

This script creates sample doctors, patients, and appointments for testing.
"""

import os
import sys
import django
from datetime import date, time, timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_appointments.settings')
django.setup()

from django.contrib.auth.models import User
from appointments.models import (
    Doctor, Patient, DoctorAvailability, Appointment, 
    ClinicSettings, TimeSlot
)


def create_sample_data():
    """Create sample data for testing."""
    
    print("Creating sample data...")
    
    # Create clinic settings
    settings, created = ClinicSettings.objects.get_or_create(
        pk=1,
        defaults={
            'clinic_name': {
                'en': 'Al-Rashid Medical Center',
                'ar': 'مركز الراشد الطبي'
            },
            'default_appointment_duration': 30,
            'advance_booking_days': 30,
            'reminder_hours_before': [24, 2],  # 24 hours and 2 hours before
            'working_hours_start': time(8, 0),
            'working_hours_end': time(17, 0),
            'timezone': 'Asia/Riyadh',
            'allow_online_booking': True,
            'require_confirmation': True,
            'max_appointments_per_day': 50
        }
    )
    
    if created:
        print("✓ Created clinic settings")
    else:
        print("✓ Clinic settings already exist")
    
    # Create time slots
    time_slots = [
        (time(8, 0), time(8, 30), 30),
        (time(8, 30), time(9, 0), 30),
        (time(9, 0), time(9, 30), 30),
        (time(9, 30), time(10, 0), 30),
        (time(10, 0), time(10, 30), 30),
        (time(10, 30), time(11, 0), 30),
        (time(11, 0), time(11, 30), 30),
        (time(11, 30), time(12, 0), 30),
        (time(13, 0), time(13, 30), 30),
        (time(13, 30), time(14, 0), 30),
        (time(14, 0), time(14, 30), 30),
        (time(14, 30), time(15, 0), 30),
        (time(15, 0), time(15, 30), 30),
        (time(15, 30), time(16, 0), 30),
        (time(16, 0), time(16, 30), 30),
        (time(16, 30), time(17, 0), 30),
    ]
    
    for start_time, end_time, duration in time_slots:
        TimeSlot.objects.get_or_create(
            start_time=start_time,
            end_time=end_time,
            defaults={'duration_minutes': duration}
        )
    
    print("✓ Created time slots")
    
    # Create doctors
    doctors_data = [
        {
            'username': 'dr_ahmed',
            'email': 'ahmed@clinic.com',
            'first_name': 'Ahmed',
            'last_name': 'Al-Rashid',
            'employee_id': 'DOC001',
            'specialization': {'en': 'Cardiology', 'ar': 'أمراض القلب'},
            'phone': '+966501234567'
        },
        {
            'username': 'dr_fatima',
            'email': 'fatima@clinic.com',
            'first_name': 'Fatima',
            'last_name': 'Al-Zahra',
            'employee_id': 'DOC002',
            'specialization': {'en': 'Pediatrics', 'ar': 'طب الأطفال'},
            'phone': '+966501234568'
        },
        {
            'username': 'dr_omar',
            'email': 'omar@clinic.com',
            'first_name': 'Omar',
            'last_name': 'Al-Mansouri',
            'employee_id': 'DOC003',
            'specialization': {'en': 'Orthopedics', 'ar': 'العظام'},
            'phone': '+966501234569'
        }
    ]
    
    doctors = []
    for doc_data in doctors_data:
        user, created = User.objects.get_or_create(
            username=doc_data['username'],
            defaults={
                'email': doc_data['email'],
                'first_name': doc_data['first_name'],
                'last_name': doc_data['last_name']
            }
        )
        
        doctor, created = Doctor.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': doc_data['employee_id'],
                'specialization': doc_data['specialization'],
                'phone': doc_data['phone']
            }
        )
        doctors.append(doctor)
        
        if created:
            print(f"✓ Created doctor: {doctor.full_name}")
        else:
            print(f"✓ Doctor already exists: {doctor.full_name}")
    
    # Create patients
    patients_data = [
        {
            'username': 'patient1',
            'email': 'patient1@example.com',
            'first_name': 'Sara',
            'last_name': 'Al-Ahmad',
            'patient_id': 'PAT001',
            'phone': '+966501111111',
            'date_of_birth': date(1985, 3, 15),
            'gender': 'F'
        },
        {
            'username': 'patient2',
            'email': 'patient2@example.com',
            'first_name': 'Mohammed',
            'last_name': 'Al-Sayed',
            'patient_id': 'PAT002',
            'phone': '+966501111112',
            'date_of_birth': date(1990, 7, 22),
            'gender': 'M'
        },
        {
            'username': 'patient3',
            'email': 'patient3@example.com',
            'first_name': 'Aisha',
            'last_name': 'Al-Rashid',
            'patient_id': 'PAT003',
            'phone': '+966501111113',
            'date_of_birth': date(1978, 11, 8),
            'gender': 'F'
        },
        {
            'username': 'patient4',
            'email': 'patient4@example.com',
            'first_name': 'Khalid',
            'last_name': 'Al-Mutairi',
            'patient_id': 'PAT004',
            'phone': '+966501111114',
            'date_of_birth': date(1995, 1, 30),
            'gender': 'M'
        }
    ]
    
    patients = []
    for pat_data in patients_data:
        user, created = User.objects.get_or_create(
            username=pat_data['username'],
            defaults={
                'email': pat_data['email'],
                'first_name': pat_data['first_name'],
                'last_name': pat_data['last_name']
            }
        )
        
        patient, created = Patient.objects.get_or_create(
            user=user,
            defaults={
                'patient_id': pat_data['patient_id'],
                'phone': pat_data['phone'],
                'date_of_birth': pat_data['date_of_birth'],
                'gender': pat_data['gender']
            }
        )
        patients.append(patient)
        
        if created:
            print(f"✓ Created patient: {patient.full_name}")
        else:
            print(f"✓ Patient already exists: {patient.full_name}")
    
    # Create doctor availability
    for doctor in doctors:
        # Monday to Friday availability
        for day in range(5):  # Monday to Friday
            DoctorAvailability.objects.get_or_create(
                doctor=doctor,
                day_of_week=day,
                start_time=time(8, 0),
                end_time=time(17, 0),
                defaults={
                    'time_slot_duration': 30,
                    'is_recurring': True,
                    'is_active': True,
                    'notes': {
                        'en': 'Regular working hours',
                        'ar': 'ساعات العمل العادية'
                    }
                }
            )
        
        # Saturday availability (half day)
        DoctorAvailability.objects.get_or_create(
            doctor=doctor,
            day_of_week=5,  # Saturday
            start_time=time(8, 0),
            end_time=time(12, 0),
            defaults={
                'time_slot_duration': 30,
                'is_recurring': True,
                'is_active': True,
                'notes': {
                    'en': 'Saturday half day',
                    'ar': 'نصف يوم السبت'
                }
            }
        )
    
    print("✓ Created doctor availability schedules")
    
    # Create sample appointments
    today = date.today()
    appointments_data = [
        {
            'patient': patients[0],
            'doctor': doctors[0],
            'appointment_date': today + timedelta(days=1),
            'appointment_time': time(9, 0),
            'reason_for_visit': {
                'en': 'Regular checkup',
                'ar': 'فحص دوري'
            },
            'notes': {
                'en': 'Patient requested morning appointment',
                'ar': 'المريض طلب موعد صباحي'
            }
        },
        {
            'patient': patients[1],
            'doctor': doctors[1],
            'appointment_date': today + timedelta(days=2),
            'appointment_time': time(10, 30),
            'reason_for_visit': {
                'en': 'Child vaccination',
                'ar': 'تطعيم الطفل'
            },
            'notes': {
                'en': 'First vaccination visit',
                'ar': 'زيارة التطعيم الأولى'
            }
        },
        {
            'patient': patients[2],
            'doctor': doctors[2],
            'appointment_date': today + timedelta(days=3),
            'appointment_time': time(14, 0),
            'reason_for_visit': {
                'en': 'Knee pain consultation',
                'ar': 'استشارة ألم الركبة'
            },
            'notes': {
                'en': 'Follow-up appointment',
                'ar': 'موعد متابعة'
            }
        },
        {
            'patient': patients[3],
            'doctor': doctors[0],
            'appointment_date': today + timedelta(days=5),
            'appointment_time': time(11, 0),
            'reason_for_visit': {
                'en': 'Heart checkup',
                'ar': 'فحص القلب'
            },
            'notes': {
                'en': 'Annual heart examination',
                'ar': 'فحص القلب السنوي'
            }
        }
    ]
    
    for apt_data in appointments_data:
        appointment, created = Appointment.objects.get_or_create(
            patient=apt_data['patient'],
            doctor=apt_data['doctor'],
            appointment_date=apt_data['appointment_date'],
            appointment_time=apt_data['appointment_time'],
            defaults={
                'reason_for_visit': apt_data['reason_for_visit'],
                'notes': apt_data['notes'],
                'duration_minutes': 30,
                'status': 'scheduled'
            }
        )
        
        if created:
            print(f"✓ Created appointment: {appointment.appointment_code}")
        else:
            print(f"✓ Appointment already exists: {appointment.appointment_code}")
    
    print("\n🎉 Sample data setup completed successfully!")
    print("\nYou can now:")
    print("1. Access the admin interface at http://localhost:8000/admin/")
    print("2. View the API documentation at http://localhost:8000/api/docs/")
    print("3. Test the API endpoints")
    print("\nSample credentials:")
    print("- Doctor: dr_ahmed / password")
    print("- Patient: patient1 / password")
    print("- Admin: Create with 'python manage.py createsuperuser'")


if __name__ == '__main__':
    create_sample_data()
