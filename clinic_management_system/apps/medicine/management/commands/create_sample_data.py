from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.medicine.models import Category, Medicine
from apps.stock.models import Stock
from apps.purchase.models import Supplier, PurchaseOrder, PurchaseOrderItem
from apps.prescription.models import Prescription, PrescriptionItem
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample data for the pharmacy management system'

    def handle(self, *args, **options):
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@pharmacy.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))

        # Create categories
        categories_data = [
            {'name_en': 'Antibiotic', 'name_ar': 'مضاد حيوي', 'description_en': 'Antibacterial medications', 'description_ar': 'أدوية مضادة للبكتيريا'},
            {'name_en': 'Painkiller', 'name_ar': 'مسكن ألم', 'description_en': 'Pain relief medications', 'description_ar': 'أدوية تسكين الألم'},
            {'name_en': 'Vitamin', 'name_ar': 'فيتامين', 'description_en': 'Vitamin supplements', 'description_ar': 'مكملات فيتامين'},
            {'name_en': 'Cardiovascular', 'name_ar': 'قلب وأوعية دموية', 'description_en': 'Heart and blood vessel medications', 'description_ar': 'أدوية القلب والأوعية الدموية'},
            {'name_en': 'Diabetes', 'name_ar': 'سكري', 'description_en': 'Diabetes medications', 'description_ar': 'أدوية السكري'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name_en=cat_data['name_en'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name_en}')

        # Create medicines
        medicines_data = [
            {
                'internal_code': 'MED001',
                'name_en': 'Amoxicillin',
                'name_ar': 'أموكسيسيلين',
                'generic_name_en': 'Amoxicillin',
                'generic_name_ar': 'أموكسيسيلين',
                'brand_name_en': 'Amoxil',
                'brand_name_ar': 'أموكسيل',
                'category': categories[0],  # Antibiotic
                'dosage_form': 'capsule',
                'strength': '500mg',
                'unit': 'box',
                'reorder_level': 10,
                'base_cost': 15.50,
                'base_selling_price': 25.00,
            },
            {
                'internal_code': 'MED002',
                'name_en': 'Paracetamol',
                'name_ar': 'باراسيتامول',
                'generic_name_en': 'Paracetamol',
                'generic_name_ar': 'باراسيتامول',
                'brand_name_en': 'Panadol',
                'brand_name_ar': 'بانادول',
                'category': categories[1],  # Painkiller
                'dosage_form': 'tablet',
                'strength': '500mg',
                'unit': 'box',
                'reorder_level': 20,
                'base_cost': 5.00,
                'base_selling_price': 8.50,
            },
            {
                'internal_code': 'MED003',
                'name_en': 'Vitamin D3',
                'name_ar': 'فيتامين د3',
                'generic_name_en': 'Cholecalciferol',
                'generic_name_ar': 'كوليكالسيفيرول',
                'brand_name_en': 'Vigantol',
                'brand_name_ar': 'فيغانتول',
                'category': categories[2],  # Vitamin
                'dosage_form': 'capsule',
                'strength': '1000 IU',
                'unit': 'box',
                'reorder_level': 15,
                'base_cost': 12.00,
                'base_selling_price': 18.00,
            },
            {
                'internal_code': 'MED004',
                'name_en': 'Metformin',
                'name_ar': 'ميتفورمين',
                'generic_name_en': 'Metformin',
                'generic_name_ar': 'ميتفورمين',
                'brand_name_en': 'Glucophage',
                'brand_name_ar': 'جلوكوفاج',
                'category': categories[4],  # Diabetes
                'dosage_form': 'tablet',
                'strength': '500mg',
                'unit': 'box',
                'reorder_level': 12,
                'base_cost': 8.50,
                'base_selling_price': 14.00,
            },
            {
                'internal_code': 'MED005',
                'name_en': 'Aspirin',
                'name_ar': 'أسبرين',
                'generic_name_en': 'Acetylsalicylic Acid',
                'generic_name_ar': 'حمض الأسيتيل الساليسيليك',
                'brand_name_en': 'Aspirin',
                'brand_name_ar': 'أسبرين',
                'category': categories[3],  # Cardiovascular
                'dosage_form': 'tablet',
                'strength': '100mg',
                'unit': 'box',
                'reorder_level': 25,
                'base_cost': 3.50,
                'base_selling_price': 6.00,
            },
        ]

        medicines = []
        for med_data in medicines_data:
            medicine, created = Medicine.objects.get_or_create(
                internal_code=med_data['internal_code'],
                defaults=med_data
            )
            medicines.append(medicine)
            if created:
                self.stdout.write(f'Created medicine: {medicine.name_en}')

        # Create suppliers
        suppliers_data = [
            {'name': 'PharmaCorp Ltd', 'contact_person': 'John Smith', 'email': 'john@pharmacorp.com', 'phone': '+1234567890'},
            {'name': 'MedSupply Inc', 'contact_person': 'Sarah Johnson', 'email': 'sarah@medsupply.com', 'phone': '+1234567891'},
            {'name': 'Global Pharma', 'contact_person': 'Ahmed Hassan', 'email': 'ahmed@globalpharma.com', 'phone': '+1234567892'},
        ]

        suppliers = []
        for sup_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=sup_data['name'],
                defaults=sup_data
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(f'Created supplier: {supplier.name}')

        # Create stock records
        admin_user = User.objects.get(username='admin')
        for medicine in medicines:
            for i in range(2):  # Create 2 stock records per medicine
                Stock.objects.get_or_create(
                    medicine=medicine,
                    batch_number=f'BATCH{medicine.internal_code}{i+1:03d}',
                    defaults={
                        'quantity': random.randint(50, 200),
                        'expiration_date': date.today() + timedelta(days=random.randint(30, 365)),
                        'purchase_cost': medicine.base_cost or 10.00,
                        'selling_price': medicine.base_selling_price or 15.00,
                        'is_active': True,
                        'stock_type': 'purchase',
                        'created_by': admin_user,
                    }
                )

        # Create a sample purchase order
        purchase_order = PurchaseOrder.objects.create(
            order_number='PO-2024-001',
            supplier=suppliers[0],
            order_date=date.today(),
            expected_delivery_date=date.today() + timedelta(days=7),
            status='received',
            tax_amount=0,
            created_by=admin_user,
        )

        # Add items to purchase order
        for medicine in medicines[:3]:  # Add first 3 medicines
            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order,
                medicine=medicine,
                quantity=random.randint(50, 100),
                received_quantity=random.randint(50, 100),
                unit_cost=medicine.base_cost or 10.00,
                batch_number=f'BATCH{medicine.internal_code}PO',
                expiration_date=date.today() + timedelta(days=random.randint(180, 365)),
                created_by=admin_user,
            )

        # Create a sample prescription
        prescription = Prescription.objects.create(
            prescription_number='RX-2024-001',
            patient_name='John Doe',
            patient_id='P001',
            doctor_name='Dr. Smith',
            doctor_id='D001',
            prescription_date=date.today(),
            status='pending',
            notes_en='Take with food',
            notes_ar='يؤخذ مع الطعام',
            created_by=admin_user,
        )

        # Add items to prescription
        for medicine in medicines[:2]:  # Add first 2 medicines
            PrescriptionItem.objects.create(
                prescription=prescription,
                medicine=medicine,
                quantity=random.randint(10, 30),
                dosage_instructions_en=f'Take {random.randint(1, 3)} tablets twice daily',
                dosage_instructions_ar=f'خذ {random.randint(1, 3)} أقراص مرتين يومياً',
                created_by=admin_user,
            )

        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
        self.stdout.write('You can now access the API documentation at: http://localhost:8000/api/docs/')

