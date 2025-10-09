"""
Inventory tests
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from .models import (
    Category, Supplier, Item, StockMovement, PurchaseOrder,
    PurchaseOrderItem, MaintenanceRecord, Alert
)


class InventoryModelTests(TestCase):
    """Test inventory models"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name_en='Medical Supplies',
            name_ar='المستلزمات الطبية'
        )
        
        self.supplier = Supplier.objects.create(
            name_en='Test Supplier',
            name_ar='مورد تجريبي',
            contact_person='John Doe',
            email='supplier@example.com',
            phone='1234567890',
            address_en='123 Test St',
            address_ar='123 شارع تجريبي'
        )
        
        self.item = Item.objects.create(
            code='SUP-001',
            name_en='Test Syringe',
            name_ar='محقنة تجريبية',
            item_type='supply',
            category=self.category,
            current_quantity=100,
            unit='pieces',
            reorder_level=20,
            location='Storage Room A',
            primary_supplier=self.supplier
        )
    
    def test_item_creation(self):
        """Test item creation"""
        self.assertEqual(self.item.name_en, 'Test Syringe')
        self.assertEqual(self.item.name_ar, 'محقنة تجريبية')
        self.assertEqual(self.item.current_quantity, 100)
        self.assertFalse(self.item.is_low_stock)
    
    def test_item_low_stock(self):
        """Test low stock detection"""
        self.item.current_quantity = 10
        self.item.save()
        self.assertTrue(self.item.is_low_stock)
    
    def test_item_expiry(self):
        """Test item expiry detection"""
        self.item.expiry_date = date.today() - timedelta(days=1)
        self.item.save()
        self.assertTrue(self.item.is_expired)
    
    def test_stock_movement_creation(self):
        """Test stock movement creation"""
        movement = StockMovement.objects.create(
            item=self.item,
            movement_type='in',
            quantity=50,
            previous_quantity=100,
            new_quantity=150,
            user=self.user,
            department='Pharmacy'
        )
        
        self.assertEqual(movement.item, self.item)
        self.assertEqual(movement.quantity, 50)
        self.assertEqual(movement.previous_quantity, 100)
        self.assertEqual(movement.new_quantity, 150)
    
    def test_purchase_order_creation(self):
        """Test purchase order creation"""
        order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            order_date=timezone.now(),
            expected_delivery=date.today() + timedelta(days=7),
            created_by=self.user
        )
        
        self.assertEqual(order.supplier, self.supplier)
        self.assertEqual(order.status, 'draft')
        self.assertTrue(order.order_number.startswith('PO-'))
    
    def test_maintenance_record_creation(self):
        """Test maintenance record creation"""
        maintenance = MaintenanceRecord.objects.create(
            item=self.item,
            maintenance_type='preventive',
            scheduled_date=timezone.now(),
            technician_name='Tech John',
            description_en='Regular maintenance',
            description_ar='صيانة دورية',
            created_by=self.user
        )
        
        self.assertEqual(maintenance.item, self.item)
        self.assertEqual(maintenance.maintenance_type, 'preventive')
        self.assertEqual(maintenance.status, 'scheduled')
    
    def test_alert_creation(self):
        """Test alert creation"""
        alert = Alert.objects.create(
            alert_type='low_stock',
            priority='high',
            item=self.item,
            title_en='Low Stock Alert',
            title_ar='تنبيه مخزون منخفض',
            message_en='Item is running low',
            message_ar='المادة تنفد'
        )
        
        self.assertEqual(alert.alert_type, 'low_stock')
        self.assertEqual(alert.priority, 'high')
        self.assertEqual(alert.item, self.item)
        self.assertFalse(alert.is_read)
        self.assertFalse(alert.is_resolved)


class InventoryAPITests(TestCase):
    """Test inventory API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name_en='Medical Supplies',
            name_ar='المستلزمات الطبية'
        )
        
        self.supplier = Supplier.objects.create(
            name_en='Test Supplier',
            name_ar='مورد تجريبي',
            contact_person='John Doe',
            email='supplier@example.com',
            phone='1234567890',
            address_en='123 Test St',
            address_ar='123 شارع تجريبي'
        )
        
        self.item = Item.objects.create(
            code='SUP-001',
            name_en='Test Syringe',
            name_ar='محقنة تجريبية',
            item_type='supply',
            category=self.category,
            current_quantity=100,
            unit='pieces',
            reorder_level=20,
            location='Storage Room A',
            primary_supplier=self.supplier
        )
    
    def test_item_list_api(self):
        """Test item list API"""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        client.force_login(self.user)
        
        response = client.get('/api/items/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Syringe')
    
    def test_item_detail_api(self):
        """Test item detail API"""
        from django.test import Client
        
        client = Client()
        client.force_login(self.user)
        
        response = client.get(f'/api/items/{self.item.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Syringe')
    
    def test_stock_adjustment_api(self):
        """Test stock adjustment API"""
        from django.test import Client
        
        client = Client()
        client.force_login(self.user)
        
        data = {
            'quantity': 50,
            'movement_type': 'adjustment',
            'notes_en': 'Test adjustment',
            'notes_ar': 'تعديل تجريبي'
        }
        
        response = client.post(f'/api/items/{self.item.id}/adjust_stock/', data)
        self.assertEqual(response.status_code, 200)
        
        # Check if quantity was updated
        self.item.refresh_from_db()
        self.assertEqual(self.item.current_quantity, 150)
    
    def test_low_stock_api(self):
        """Test low stock API"""
        from django.test import Client
        
        # Set item to low stock
        self.item.current_quantity = 10
        self.item.save()
        
        client = Client()
        client.force_login(self.user)
        
        response = client.get('/api/items/low_stock/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Syringe')


class InventoryIntegrationTests(TestCase):
    """Test integration functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name_en='Medical Supplies',
            name_ar='المستلزمات الطبية'
        )
        
        self.supplier = Supplier.objects.create(
            name_en='Test Supplier',
            name_ar='مورد تجريبي',
            contact_person='John Doe',
            email='supplier@example.com',
            phone='1234567890',
            address_en='123 Test St',
            address_ar='123 شارع تجريبي'
        )
        
        self.item = Item.objects.create(
            code='SUP-001',
            name_en='Test Syringe',
            name_ar='محقنة تجريبية',
            item_type='supply',
            category=self.category,
            current_quantity=100,
            unit='pieces',
            reorder_level=20,
            location='Storage Room A',
            primary_supplier=self.supplier
        )
    
    def test_pharmacy_integration(self):
        """Test pharmacy integration API"""
        from django.test import Client
        
        client = Client()
        client.force_login(self.user)
        
        data = {
            'items': [
                {
                    'item_code': 'SUP-001',
                    'quantity': 10,
                    'notes_en': 'Pharmacy request',
                    'notes_ar': 'طلب صيدلية'
                }
            ],
            'reference_number': 'PHARM-001'
        }
        
        response = client.post('/api/items/pharmacy_request/', data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        # Check if stock was reduced
        self.item.refresh_from_db()
        self.assertEqual(self.item.current_quantity, 90)
    
    def test_laboratory_integration(self):
        """Test laboratory integration API"""
        from django.test import Client
        
        client = Client()
        client.force_login(self.user)
        
        data = {
            'items': [
                {
                    'item_code': 'SUP-001',
                    'quantity': 5,
                    'notes_en': 'Laboratory request',
                    'notes_ar': 'طلب مختبر'
                }
            ],
            'reference_number': 'LAB-001'
        }
        
        response = client.post('/api/items/laboratory_request/', data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        # Check if stock was reduced
        self.item.refresh_from_db()
        self.assertEqual(self.item.current_quantity, 95)
    
    def test_available_items_api(self):
        """Test available items API"""
        from django.test import Client
        
        client = Client()
        client.force_login(self.user)
        
        response = client.get('/api/items/available_items/?department=pharmacy')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Syringe')
    
    def test_stock_status_api(self):
        """Test stock status API"""
        from django.test import Client
        
        client = Client()
        client.force_login(self.user)
        
        response = client.get('/api/items/stock_status/?item_codes=SUP-001')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Syringe')
        self.assertContains(response, '100')
