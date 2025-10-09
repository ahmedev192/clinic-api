"""
Management command to seed initial data for the billing system.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from billing.models import (
    Patient, Doctor, ServiceCategory, Service, PaymentMethod, Discount
)


class Command(BaseCommand):
    help = 'Seed initial data for the billing system'

    def handle(self, *args, **options):
        self.stdout.write('Seeding initial data...')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@clinic.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Create sample patients
        patients_data = [
            {
                'patient_id': 'P001',
                'first_name_en': 'Ahmed',
                'first_name_ar': 'أحمد',
                'last_name_en': 'Hassan',
                'last_name_ar': 'حسن',
                'phone': '+966501234567',
                'email': 'ahmed.hassan@email.com'
            },
            {
                'patient_id': 'P002',
                'first_name_en': 'Fatima',
                'first_name_ar': 'فاطمة',
                'last_name_en': 'Ali',
                'last_name_ar': 'علي',
                'phone': '+966501234568',
                'email': 'fatima.ali@email.com'
            },
            {
                'patient_id': 'P003',
                'first_name_en': 'Mohammed',
                'first_name_ar': 'محمد',
                'last_name_en': 'Omar',
                'last_name_ar': 'عمر',
                'phone': '+966501234569',
                'email': 'mohammed.omar@email.com'
            }
        ]
        
        for patient_data in patients_data:
            patient, created = Patient.objects.get_or_create(
                patient_id=patient_data['patient_id'],
                defaults=patient_data
            )
            if created:
                self.stdout.write(f'Created patient: {patient.full_name_en}')
        
        # Create sample doctors
        doctors_data = [
            {
                'doctor_id': 'D001',
                'first_name_en': 'Dr. Sarah',
                'first_name_ar': 'د. سارة',
                'last_name_en': 'Johnson',
                'last_name_ar': 'جونسون',
                'specialization_en': 'General Medicine',
                'specialization_ar': 'الطب العام',
                'license_number': 'MD123456'
            },
            {
                'doctor_id': 'D002',
                'first_name_en': 'Dr. Khalid',
                'first_name_ar': 'د. خالد',
                'last_name_en': 'Al-Rashid',
                'last_name_ar': 'الرشيد',
                'specialization_en': 'Cardiology',
                'specialization_ar': 'أمراض القلب',
                'license_number': 'MD123457'
            },
            {
                'doctor_id': 'D003',
                'first_name_en': 'Dr. Aisha',
                'first_name_ar': 'د. عائشة',
                'last_name_en': 'Al-Zahra',
                'last_name_ar': 'الزهراء',
                'specialization_en': 'Pediatrics',
                'specialization_ar': 'طب الأطفال',
                'license_number': 'MD123458'
            }
        ]
        
        for doctor_data in doctors_data:
            doctor, created = Doctor.objects.get_or_create(
                doctor_id=doctor_data['doctor_id'],
                defaults=doctor_data
            )
            if created:
                self.stdout.write(f'Created doctor: {doctor.full_name_en}')
        
        # Create service categories
        categories_data = [
            {
                'name_en': 'Consultations',
                'name_ar': 'الاستشارات',
                'description_en': 'Medical consultations and examinations',
                'description_ar': 'الاستشارات والفحوصات الطبية'
            },
            {
                'name_en': 'Laboratory Tests',
                'name_ar': 'الفحوصات المخبرية',
                'description_en': 'Blood tests, urine tests, and other lab work',
                'description_ar': 'فحوصات الدم والبول والفحوصات المخبرية الأخرى'
            },
            {
                'name_en': 'Pharmacy',
                'name_ar': 'الصيدلية',
                'description_en': 'Medications and pharmaceutical products',
                'description_ar': 'الأدوية والمنتجات الصيدلانية'
            },
            {
                'name_en': 'Procedures',
                'name_ar': 'الإجراءات',
                'description_en': 'Medical procedures and treatments',
                'description_ar': 'الإجراءات والعلاجات الطبية'
            }
        ]
        
        for category_data in categories_data:
            category, created = ServiceCategory.objects.get_or_create(
                name_en=category_data['name_en'],
                defaults=category_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name_en}')
        
        # Create services
        services_data = [
            {
                'service_id': 'S001',
                'name_en': 'General Consultation',
                'name_ar': 'استشارة عامة',
                'description_en': 'General medical consultation with doctor',
                'description_ar': 'استشارة طبية عامة مع الطبيب',
                'category': 'Consultations',
                'service_type': 'consultation',
                'base_price': 150.00
            },
            {
                'service_id': 'S002',
                'name_en': 'Blood Test - Complete',
                'name_ar': 'فحص دم شامل',
                'description_en': 'Complete blood count test',
                'description_ar': 'فحص تعداد الدم الكامل',
                'category': 'Laboratory Tests',
                'service_type': 'lab_test',
                'base_price': 75.00
            },
            {
                'service_id': 'S003',
                'name_en': 'X-Ray - Chest',
                'name_ar': 'أشعة سينية - صدر',
                'description_en': 'Chest X-ray examination',
                'description_ar': 'فحص أشعة سينية للصدر',
                'category': 'Procedures',
                'service_type': 'procedure',
                'base_price': 200.00
            },
            {
                'service_id': 'S004',
                'name_en': 'Prescription Medicine',
                'name_ar': 'دواء موصوف',
                'description_en': 'Prescribed medication',
                'description_ar': 'دواء موصوف من الطبيب',
                'category': 'Pharmacy',
                'service_type': 'pharmacy',
                'base_price': 50.00
            }
        ]
        
        for service_data in services_data:
            category = ServiceCategory.objects.get(name_en=service_data['category'])
            service_data['category'] = category
            service, created = Service.objects.get_or_create(
                service_id=service_data['service_id'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'Created service: {service.name_en}')
        
        # Create payment methods
        payment_methods_data = [
            {
                'name_en': 'Cash',
                'name_ar': 'نقداً',
                'payment_type': 'cash',
                'requires_reference': False
            },
            {
                'name_en': 'Credit Card',
                'name_ar': 'بطاقة ائتمان',
                'payment_type': 'card',
                'requires_reference': True
            },
            {
                'name_en': 'Bank Transfer',
                'name_ar': 'تحويل بنكي',
                'payment_type': 'bank_transfer',
                'requires_reference': True
            },
            {
                'name_en': 'Mobile Wallet',
                'name_ar': 'محفظة إلكترونية',
                'payment_type': 'mobile_wallet',
                'requires_reference': True
            },
            {
                'name_en': 'Insurance',
                'name_ar': 'تأمين',
                'payment_type': 'insurance',
                'requires_reference': True
            }
        ]
        
        for method_data in payment_methods_data:
            method, created = PaymentMethod.objects.get_or_create(
                name_en=method_data['name_en'],
                defaults=method_data
            )
            if created:
                self.stdout.write(f'Created payment method: {method.name_en}')
        
        # Create sample discounts
        discounts_data = [
            {
                'name_en': 'New Patient Discount',
                'name_ar': 'خصم المريض الجديد',
                'description_en': '10% discount for new patients',
                'description_ar': 'خصم 10% للمرضى الجدد',
                'discount_type': 'percentage',
                'value': 10.00,
                'min_invoice_amount': 100.00,
                'is_active': True
            },
            {
                'name_en': 'Senior Citizen Discount',
                'name_ar': 'خصم كبار السن',
                'description_en': '15% discount for senior citizens',
                'description_ar': 'خصم 15% لكبار السن',
                'discount_type': 'percentage',
                'value': 15.00,
                'min_invoice_amount': 50.00,
                'is_active': True
            },
            {
                'name_en': 'Fixed Amount Discount',
                'name_ar': 'خصم مبلغ ثابت',
                'description_en': 'Fixed 50 SAR discount',
                'description_ar': 'خصم ثابت 50 ريال',
                'discount_type': 'fixed',
                'value': 50.00,
                'max_discount_amount': 50.00,
                'min_invoice_amount': 200.00,
                'is_active': True
            }
        ]
        
        admin_user = User.objects.get(username='admin')
        for discount_data in discounts_data:
            discount, created = Discount.objects.get_or_create(
                name_en=discount_data['name_en'],
                defaults={**discount_data, 'created_by': admin_user}
            )
            if created:
                self.stdout.write(f'Created discount: {discount.name_en}')
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded initial data!'))
