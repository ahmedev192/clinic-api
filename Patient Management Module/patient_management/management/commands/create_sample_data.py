"""
Django management command to create sample patient data for testing.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from patient_management.models import Patient, MedicalHistory, Allergy, ChronicCondition, PatientDocument
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample patient data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of patients to create (default: 10)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before creating new data'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        
        if clear:
            self.stdout.write('Clearing existing sample data...')
            Patient.objects.filter(patient_code__startswith='PAT-2024-').delete()
        
        # Create a test user if it doesn't exist
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        self.stdout.write(f'Creating {count} sample patients...')
        
        # Sample data
        first_names_en = [
            'Ahmed', 'Mohammed', 'Ali', 'Omar', 'Hassan', 'Ibrahim', 'Youssef', 'Khalid',
            'Sarah', 'Fatima', 'Aisha', 'Mariam', 'Nour', 'Layla', 'Zainab', 'Amina'
        ]
        
        first_names_ar = [
            'أحمد', 'محمد', 'علي', 'عمر', 'حسن', 'إبراهيم', 'يوسف', 'خالد',
            'سارة', 'فاطمة', 'عائشة', 'مريم', 'نور', 'ليلى', 'زينب', 'أمينة'
        ]
        
        last_names_en = [
            'Al-Rashid', 'Al-Mansour', 'Al-Abbas', 'Al-Hassan', 'Al-Hussein',
            'Al-Zahra', 'Al-Fatima', 'Al-Aisha', 'Al-Mariam', 'Al-Nour'
        ]
        
        last_names_ar = [
            'الرشيد', 'المنصور', 'العباس', 'الحسن', 'الحسين',
            'الزهراء', 'فاطمة', 'عائشة', 'مريم', 'نور'
        ]
        
        cities = ['Riyadh', 'Jeddah', 'Mecca', 'Medina', 'Dammam', 'Khobar', 'Dhahran']
        cities_ar = ['الرياض', 'جدة', 'مكة', 'المدينة', 'الدمام', 'الخبر', 'الظهران']
        
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        # Medical conditions
        conditions = [
            ('diabetes', 'Diabetes', 'السكري'),
            ('hypertension', 'Hypertension', 'ارتفاع ضغط الدم'),
            ('asthma', 'Asthma', 'الربو'),
            ('heart_disease', 'Heart Disease', 'أمراض القلب'),
            ('arthritis', 'Arthritis', 'التهاب المفاصل')
        ]
        
        allergies = [
            ('penicillin', 'Penicillin', 'البنسلين'),
            ('sulfa', 'Sulfa Drugs', 'أدوية السلفا'),
            ('nuts', 'Nuts', 'المكسرات'),
            ('shellfish', 'Shellfish', 'المأكولات البحرية'),
            ('pollen', 'Pollen', 'حبوب اللقاح')
        ]
        
        for i in range(count):
            # Generate random data
            first_name_en = random.choice(first_names_en)
            first_name_ar = random.choice(first_names_ar)
            last_name_en = random.choice(last_names_en)
            last_name_ar = random.choice(last_names_ar)
            
            # Generate birth date (18-80 years old)
            birth_year = random.randint(1944, 2006)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            birth_date = date(birth_year, birth_month, birth_day)
            
            # Generate phone number
            phone_number = f'+9665{random.randint(10000000, 99999999)}'
            
            # Generate national ID
            national_id = f'{random.randint(1000000000, 9999999999)}'
            
            # Create patient
            patient = Patient.objects.create(
                first_name_en=first_name_en,
                first_name_ar=first_name_ar,
                last_name_en=last_name_en,
                last_name_ar=last_name_ar,
                gender=random.choice(['M', 'F']),
                date_of_birth=birth_date,
                phone_number=phone_number,
                email=f'{first_name_en.lower()}.{last_name_en.lower()}@example.com',
                address_en=f'{random.randint(1, 999)} Main Street, District {random.randint(1, 20)}',
                address_ar=f'شارع الرئيسي {random.randint(1, 999)}، حي {random.randint(1, 20)}',
                city=random.choice(cities),
                state_province='Riyadh Province',
                postal_code=f'{random.randint(10000, 99999)}',
                country='Saudi Arabia',
                national_id=national_id,
                blood_type=random.choice(blood_types),
                emergency_contact_name=f'Emergency Contact {i+1}',
                emergency_contact_phone=f'+9665{random.randint(10000000, 99999999)}',
                emergency_contact_relationship='Family Member',
                notes=f'Sample patient {i+1} created for testing',
                created_by=user,
                updated_by=user
            )
            
            # Create medical history entries
            for j in range(random.randint(1, 3)):
                MedicalHistory.objects.create(
                    patient=patient,
                    category=random.choice(['diagnosis', 'treatment', 'hospitalization']),
                    title_en=f'Medical Event {j+1}',
                    title_ar=f'حدث طبي {j+1}',
                    description_en=f'Description of medical event {j+1}',
                    description_ar=f'وصف الحدث الطبي {j+1}',
                    event_date=birth_date + timedelta(days=random.randint(1, 1000)),
                    created_by=user,
                    updated_by=user
                )
            
            # Create allergies
            if random.choice([True, False]):
                allergy_data = random.choice(allergies)
                Allergy.objects.create(
                    patient=patient,
                    allergy_type=random.choice(['medication', 'food', 'environmental']),
                    allergen_en=allergy_data[1],
                    allergen_ar=allergy_data[2],
                    description_en=f'Allergic reaction to {allergy_data[1]}',
                    description_ar=f'رد فعل تحسسي تجاه {allergy_data[2]}',
                    severity=random.choice(['mild', 'moderate', 'severe']),
                    symptoms='Rash, itching, difficulty breathing',
                    created_by=user,
                    updated_by=user
                )
            
            # Create chronic conditions
            if random.choice([True, False]):
                condition_data = random.choice(conditions)
                ChronicCondition.objects.create(
                    patient=patient,
                    condition_type=condition_data[0],
                    condition_name_en=condition_data[1],
                    condition_name_ar=condition_data[2],
                    description_en=f'Chronic {condition_data[1]} condition',
                    description_ar=f'حالة مزمنة من {condition_data[2]}',
                    severity=random.choice(['mild', 'moderate', 'severe']),
                    diagnosis_date=birth_date + timedelta(days=random.randint(100, 2000)),
                    is_active=random.choice([True, False]),
                    created_by=user,
                    updated_by=user
                )
            
            self.stdout.write(f'Created patient: {patient.patient_code} - {patient.get_full_name()}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count} sample patients!')
        )
