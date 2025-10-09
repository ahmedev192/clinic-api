#!/usr/bin/env python
"""
Data seeding script for Clinic Inventory & Asset Management Module
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Seed the database with sample data"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_inventory.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    from inventory.models import Category, Supplier, Item
    
    print("Seeding database with sample data...")
    
    # Create categories
    categories_data = [
        {'name_en': 'Medical Supplies', 'name_ar': 'المستلزمات الطبية'},
        {'name_en': 'Surgical Instruments', 'name_ar': 'الأدوات الجراحية'},
        {'name_en': 'Laboratory Equipment', 'name_ar': 'معدات المختبر'},
        {'name_en': 'Diagnostic Equipment', 'name_ar': 'معدات التشخيص'},
        {'name_en': 'Furniture', 'name_ar': 'الأثاث'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name_en=cat_data['name_en'],
            defaults=cat_data
        )
        categories.append(category)
        if created:
            print(f"Created category: {category.name_en}")
    
    # Create suppliers
    suppliers_data = [
        {
            'name_en': 'MedSupply Co.', 'name_ar': 'شركة ميدسابلاي',
            'contact_person': 'Ahmed Hassan', 'email': 'ahmed@medsupply.com',
            'phone': '+966501234567', 'address_en': 'Riyadh, Saudi Arabia',
            'address_ar': 'الرياض، المملكة العربية السعودية'
        },
        {
            'name_en': 'Global Medical', 'name_ar': 'جلوبال ميديكال',
            'contact_person': 'Sarah Johnson', 'email': 'sarah@globalmed.com',
            'phone': '+966502345678', 'address_en': 'Jeddah, Saudi Arabia',
            'address_ar': 'جدة، المملكة العربية السعودية'
        },
        {
            'name_en': 'Lab Equipment Ltd.', 'name_ar': 'معدات المختبر المحدودة',
            'contact_person': 'Mohammed Ali', 'email': 'mohammed@labeq.com',
            'phone': '+966503456789', 'address_en': 'Dammam, Saudi Arabia',
            'address_ar': 'الدمام، المملكة العربية السعودية'
        }
    ]
    
    suppliers = []
    for sup_data in suppliers_data:
        supplier, created = Supplier.objects.get_or_create(
            name_en=sup_data['name_en'],
            defaults=sup_data
        )
        suppliers.append(supplier)
        if created:
            print(f"Created supplier: {supplier.name_en}")
    
    # Create sample items
    items_data = [
        {
            'code': 'SUP-001', 'name_en': 'Disposable Syringes 5ml', 'name_ar': 'محاقن 5 مل قابلة للتصرف',
            'item_type': 'supply', 'category': categories[0], 'current_quantity': 500,
            'unit': 'pieces', 'reorder_level': 100, 'location': 'Storage Room A',
            'primary_supplier': suppliers[0], 'unit_cost': 2.50
        },
        {
            'code': 'SUP-002', 'name_en': 'Surgical Gloves (Large)', 'name_ar': 'قفازات جراحية (كبير)',
            'item_type': 'supply', 'category': categories[0], 'current_quantity': 1000,
            'unit': 'pairs', 'reorder_level': 200, 'location': 'Storage Room A',
            'primary_supplier': suppliers[0], 'unit_cost': 1.20
        },
        {
            'code': 'EQP-001', 'name_en': 'Blood Pressure Monitor', 'name_ar': 'جهاز قياس ضغط الدم',
            'item_type': 'equipment', 'category': categories[3], 'current_quantity': 5,
            'unit': 'units', 'reorder_level': 1, 'location': 'Examination Room 1',
            'primary_supplier': suppliers[1], 'unit_cost': 150.00
        },
        {
            'code': 'EQP-002', 'name_en': 'Microscope', 'name_ar': 'مجهر',
            'item_type': 'equipment', 'category': categories[2], 'current_quantity': 2,
            'unit': 'units', 'reorder_level': 1, 'location': 'Laboratory',
            'primary_supplier': suppliers[2], 'unit_cost': 2500.00
        },
        {
            'code': 'TOL-001', 'name_en': 'Surgical Scissors', 'name_ar': 'مقص جراحي',
            'item_type': 'tool', 'category': categories[1], 'current_quantity': 20,
            'unit': 'pieces', 'reorder_level': 5, 'location': 'Surgery Room',
            'primary_supplier': suppliers[1], 'unit_cost': 25.00
        },
        {
            'code': 'CON-001', 'name_en': 'Cotton Swabs', 'name_ar': 'مسحات قطنية',
            'item_type': 'consumable', 'category': categories[0], 'current_quantity': 2000,
            'unit': 'pieces', 'reorder_level': 500, 'location': 'Storage Room B',
            'primary_supplier': suppliers[0], 'unit_cost': 0.50
        },
        {
            'code': 'FUR-001', 'name_en': 'Examination Table', 'name_ar': 'طاولة فحص',
            'item_type': 'furniture', 'category': categories[4], 'current_quantity': 3,
            'unit': 'units', 'reorder_level': 1, 'location': 'Examination Room 2',
            'primary_supplier': suppliers[1], 'unit_cost': 800.00
        }
    ]
    
    for item_data in items_data:
        item, created = Item.objects.get_or_create(
            code=item_data['code'],
            defaults=item_data
        )
        if created:
            print(f"Created item: {item.name_en}")
    
    print("\nSample data seeded successfully!")
    print("You can now access the admin panel at http://localhost:8000/admin/")
    print("Username: admin")
    print("Password: admin123")

if __name__ == '__main__':
    main()
