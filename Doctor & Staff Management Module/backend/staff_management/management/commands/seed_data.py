"""
Management command to seed initial data for staff management
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from staff_management.models import Role, Specialization, Staff, Doctor, Schedule, Compensation
from datetime import date, time, timedelta
import random


class Command(BaseCommand):
    help = 'Seed initial data for staff management system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()
        
        self.stdout.write('Seeding initial data...')
        
        # Create roles
        self.create_roles()
        
        # Create specializations
        self.create_specializations()
        
        # Create admin user
        self.create_admin_user()
        
        # Create sample staff
        self.create_sample_staff()
        
        # Create doctor profiles
        self.create_doctor_profiles()
        
        # Create schedules
        self.create_schedules()
        
        # Create compensations
        self.create_compensations()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded initial data!')
        )
    
    def clear_data(self):
        """Clear existing data"""
        Staff.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Role.objects.all().delete()
        Specialization.objects.all().delete()
    
    def create_roles(self):
        """Create staff roles"""
        roles_data = [
            {
                'code': 'ADMIN',
                'name_en': 'Administrator',
                'name_ar': 'مدير',
                'description_en': 'Full system access and management',
                'description_ar': 'وصول كامل للنظام والإدارة'
            },
            {
                'code': 'DOC',
                'name_en': 'Doctor',
                'name_ar': 'طبيب',
                'description_en': 'Medical doctor with patient care responsibilities',
                'description_ar': 'طبيب مع مسؤوليات رعاية المرضى'
            },
            {
                'code': 'NURSE',
                'name_en': 'Nurse',
                'name_ar': 'ممرض/ممرضة',
                'description_en': 'Nursing staff for patient care',
                'description_ar': 'طاقم التمريض لرعاية المرضى'
            },
            {
                'code': 'RECEPTIONIST',
                'name_en': 'Receptionist',
                'name_ar': 'موظف استقبال',
                'description_en': 'Front desk and appointment management',
                'description_ar': 'مكتب الاستقبال وإدارة المواعيد'
            },
            {
                'code': 'PHARMACIST',
                'name_en': 'Pharmacist',
                'name_ar': 'صيدلي',
                'description_en': 'Pharmacy and medication management',
                'description_ar': 'إدارة الصيدلية والأدوية'
            },
            {
                'code': 'LAB_TECH',
                'name_en': 'Lab Technician',
                'name_ar': 'فني مختبر',
                'description_en': 'Laboratory testing and analysis',
                'description_ar': 'الفحوصات المخبرية والتحليل'
            },
            {
                'code': 'MANAGER',
                'name_en': 'Manager',
                'name_ar': 'مدير',
                'description_en': 'Department or clinic manager',
                'description_ar': 'مدير القسم أو العيادة'
            }
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                code=role_data['code'],
                defaults=role_data
            )
            if created:
                self.stdout.write(f'Created role: {role.name_en}')
    
    def create_specializations(self):
        """Create medical specializations"""
        specializations_data = [
            {
                'name_en': 'Cardiology',
                'name_ar': 'أمراض القلب',
                'description_en': 'Heart and cardiovascular system diseases',
                'description_ar': 'أمراض القلب والجهاز الدوري'
            },
            {
                'name_en': 'Dermatology',
                'name_ar': 'الأمراض الجلدية',
                'description_en': 'Skin, hair, and nail conditions',
                'description_ar': 'حالات الجلد والشعر والأظافر'
            },
            {
                'name_en': 'Pediatrics',
                'name_ar': 'طب الأطفال',
                'description_en': 'Medical care for infants, children, and adolescents',
                'description_ar': 'الرعاية الطبية للرضع والأطفال والمراهقين'
            },
            {
                'name_en': 'Orthopedics',
                'name_ar': 'العظام',
                'description_en': 'Bone, joint, and muscle disorders',
                'description_ar': 'اضطرابات العظام والمفاصل والعضلات'
            },
            {
                'name_en': 'Gynecology',
                'name_ar': 'أمراض النساء',
                'description_en': 'Women\'s reproductive health',
                'description_ar': 'صحة المرأة الإنجابية'
            },
            {
                'name_en': 'Internal Medicine',
                'name_ar': 'الطب الباطني',
                'description_en': 'Adult internal organ diseases',
                'description_ar': 'أمراض الأعضاء الداخلية للبالغين'
            },
            {
                'name_en': 'Ophthalmology',
                'name_ar': 'طب العيون',
                'description_en': 'Eye and vision care',
                'description_ar': 'رعاية العين والرؤية'
            },
            {
                'name_en': 'ENT',
                'name_ar': 'أنف وأذن وحنجرة',
                'description_en': 'Ear, nose, and throat conditions',
                'description_ar': 'حالات الأذن والأنف والحنجرة'
            }
        ]
        
        for spec_data in specializations_data:
            spec, created = Specialization.objects.get_or_create(
                name_en=spec_data['name_en'],
                defaults=spec_data
            )
            if created:
                self.stdout.write(f'Created specialization: {spec.name_en}')
    
    def create_admin_user(self):
        """Create admin user"""
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@clinic.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user')
    
    def create_sample_staff(self):
        """Create sample staff members"""
        # Get roles
        admin_role = Role.objects.get(code='ADMIN')
        doctor_role = Role.objects.get(code='DOC')
        nurse_role = Role.objects.get(code='NURSE')
        receptionist_role = Role.objects.get(code='RECEPTIONIST')
        
        # Sample staff data
        staff_data = [
            {
                'username': 'dr_smith',
                'email': 'dr.smith@clinic.com',
                'first_name_en': 'John',
                'first_name_ar': 'جون',
                'last_name_en': 'Smith',
                'last_name_ar': 'سميث',
                'role': doctor_role,
                'gender': 'M',
                'phone_primary': '+966501234567',
                'address_en': '123 King Fahd Road, Riyadh',
                'address_ar': '123 طريق الملك فهد، الرياض',
                'city': 'Riyadh',
                'national_id': '1234567890'
            },
            {
                'username': 'dr_ahmed',
                'email': 'dr.ahmed@clinic.com',
                'first_name_en': 'Ahmed',
                'first_name_ar': 'أحمد',
                'last_name_en': 'Al-Rashid',
                'last_name_ar': 'الرشيد',
                'role': doctor_role,
                'gender': 'M',
                'phone_primary': '+966501234568',
                'address_en': '456 Prince Mohammed Road, Jeddah',
                'address_ar': '456 طريق الأمير محمد، جدة',
                'city': 'Jeddah',
                'national_id': '1234567891'
            },
            {
                'username': 'nurse_sarah',
                'email': 'sarah@clinic.com',
                'first_name_en': 'Sarah',
                'first_name_ar': 'سارة',
                'last_name_en': 'Johnson',
                'last_name_ar': 'جونسون',
                'role': nurse_role,
                'gender': 'F',
                'phone_primary': '+966501234569',
                'address_en': '789 Al-Malaz Road, Riyadh',
                'address_ar': '789 طريق الملز، الرياض',
                'city': 'Riyadh',
                'national_id': '1234567892'
            },
            {
                'username': 'reception_fatima',
                'email': 'fatima@clinic.com',
                'first_name_en': 'Fatima',
                'first_name_ar': 'فاطمة',
                'last_name_en': 'Al-Zahra',
                'last_name_ar': 'الزهراء',
                'role': receptionist_role,
                'gender': 'F',
                'phone_primary': '+966501234570',
                'address_en': '321 Al-Olaya Road, Riyadh',
                'address_ar': '321 طريق العليا، الرياض',
                'city': 'Riyadh',
                'national_id': '1234567893'
            }
        ]
        
        for data in staff_data:
            # Create user
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name_en'],
                    'last_name': data['last_name_en']
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            
            # Create staff profile
            staff, created = Staff.objects.get_or_create(
                user=user,
                defaults={
                    'role': data['role'],
                    'first_name_en': data['first_name_en'],
                    'first_name_ar': data['first_name_ar'],
                    'last_name_en': data['last_name_en'],
                    'last_name_ar': data['last_name_ar'],
                    'email': data['email'],
                    'phone_primary': data['phone_primary'],
                    'address_en': data['address_en'],
                    'address_ar': data['address_ar'],
                    'city': data['city'],
                    'country': 'Saudi Arabia',
                    'gender': data['gender'],
                    'date_of_birth': date(1980, 1, 1),
                    'national_id': data['national_id'],
                    'employment_status': 'active',
                    'joining_date': date(2020, 1, 1),
                    'created_by': User.objects.get(username='admin')
                }
            )
            if created:
                self.stdout.write(f'Created staff: {staff.full_name_en}')
    
    def create_doctor_profiles(self):
        """Create doctor profiles for doctor staff"""
        doctors = Staff.objects.filter(role__code='DOC')
        specializations = list(Specialization.objects.all())
        
        for doctor_staff in doctors:
            doctor, created = Doctor.objects.get_or_create(
                staff=doctor_staff,
                defaults={
                    'medical_license_number': f'ML{random.randint(100000, 999999)}',
                    'professional_title_en': 'Dr.',
                    'professional_title_ar': 'د.',
                    'years_of_experience': random.randint(5, 25),
                    'biography_en': f'Experienced doctor specializing in patient care.',
                    'biography_ar': f'طبيب ذو خبرة متخصص في رعاية المرضى.',
                    'languages': ['English', 'Arabic'],
                    'consultation_fee': round(random.uniform(200, 500), 2),
                    'hourly_rate': round(random.uniform(100, 300), 2),
                    'is_available': True,
                    'is_accepting_new_patients': True
                }
            )
            if created:
                # Assign random specializations
                num_specs = random.randint(1, 3)
                selected_specs = random.sample(specializations, min(num_specs, len(specializations)))
                doctor.specializations.set(selected_specs)
                self.stdout.write(f'Created doctor profile: {doctor.staff.full_name_en}')
    
    def create_schedules(self):
        """Create sample schedules for staff"""
        staff_members = Staff.objects.all()
        days = [0, 1, 2, 3, 4]  # Monday to Friday
        
        for staff in staff_members:
            for day in days:
                # Create morning shift (9 AM - 1 PM)
                Schedule.objects.get_or_create(
                    staff=staff,
                    day_of_week=day,
                    start_time=time(9, 0),
                    defaults={
                        'end_time': time(13, 0),
                        'is_active': True,
                        'notes': 'Morning shift'
                    }
                )
                
                # Create afternoon shift (2 PM - 6 PM)
                Schedule.objects.get_or_create(
                    staff=staff,
                    day_of_week=day,
                    start_time=time(14, 0),
                    defaults={
                        'end_time': time(18, 0),
                        'is_active': True,
                        'notes': 'Afternoon shift'
                    }
                )
        
        self.stdout.write('Created sample schedules')
    
    def create_compensations(self):
        """Create sample compensations for staff"""
        staff_members = Staff.objects.all()
        
        for staff in staff_members:
            compensation_type = random.choice(['salary', 'mixed'])
            base_salary = round(random.uniform(5000, 15000), 2) if compensation_type in ['salary', 'mixed'] else None
            commission_percentage = round(random.uniform(5, 15), 2) if compensation_type in ['commission', 'mixed'] else None
            
            Compensation.objects.get_or_create(
                staff=staff,
                defaults={
                    'compensation_type': compensation_type,
                    'base_salary': base_salary,
                    'commission_percentage': commission_percentage,
                    'effective_from': date(2020, 1, 1),
                    'notes': f'Initial compensation for {staff.full_name_en}'
                }
            )
        
        self.stdout.write('Created sample compensations')
