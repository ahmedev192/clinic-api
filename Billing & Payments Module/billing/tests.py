"""
Tests for billing models and API.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import (
    Patient, Doctor, ServiceCategory, Service, Invoice, InvoiceItem,
    PaymentMethod, Payment, Refund, Discount, AuditLog
)


class BillingModelsTestCase(TestCase):
    """Test cases for billing models."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.patient = Patient.objects.create(
            patient_id='P001',
            first_name_en='Ahmed',
            first_name_ar='أحمد',
            last_name_en='Hassan',
            last_name_ar='حسن',
            phone='+966501234567',
            email='ahmed@example.com'
        )
        
        self.doctor = Doctor.objects.create(
            doctor_id='D001',
            first_name_en='Dr. Sarah',
            first_name_ar='د. سارة',
            last_name_en='Johnson',
            last_name_ar='جونسون',
            specialization_en='General Medicine',
            specialization_ar='الطب العام',
            license_number='MD123456'
        )
        
        self.category = ServiceCategory.objects.create(
            name_en='Consultations',
            name_ar='الاستشارات',
            description_en='Medical consultations',
            description_ar='الاستشارات الطبية'
        )
        
        self.service = Service.objects.create(
            service_id='S001',
            name_en='General Consultation',
            name_ar='استشارة عامة',
            description_en='General medical consultation',
            description_ar='استشارة طبية عامة',
            category=self.category,
            service_type='consultation',
            base_price=Decimal('150.00')
        )
        
        self.payment_method = PaymentMethod.objects.create(
            name_en='Cash',
            name_ar='نقداً',
            payment_type='cash',
            requires_reference=False
        )

    def test_patient_creation(self):
        """Test patient model creation."""
        self.assertEqual(self.patient.full_name_en, 'Ahmed Hassan')
        self.assertEqual(self.patient.full_name_ar, 'أحمد حسن')
        self.assertEqual(str(self.patient), 'Ahmed Hassan (P001)')

    def test_doctor_creation(self):
        """Test doctor model creation."""
        self.assertEqual(self.doctor.full_name_en, 'Dr. Sarah Johnson')
        self.assertEqual(self.doctor.full_name_ar, 'د. سارة جونسون')
        self.assertEqual(str(self.doctor), 'Dr. Sarah Johnson')

    def test_service_creation(self):
        """Test service model creation."""
        self.assertEqual(str(self.service), 'General Consultation | استشارة عامة')
        self.assertEqual(self.service.base_price, Decimal('150.00'))

    def test_invoice_creation(self):
        """Test invoice model creation."""
        invoice = Invoice.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            invoice_date=timezone.now(),
            created_by=self.user
        )
        
        self.assertEqual(invoice.patient, self.patient)
        self.assertEqual(invoice.doctor, self.doctor)
        self.assertEqual(invoice.status, Invoice.INVOICE_STATUS.draft)

    def test_invoice_item_creation(self):
        """Test invoice item model creation."""
        invoice = Invoice.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            invoice_date=timezone.now(),
            created_by=self.user
        )
        
        item = InvoiceItem.objects.create(
            invoice=invoice,
            service=self.service,
            description_en='Test consultation',
            description_ar='استشارة تجريبية',
            quantity=1,
            unit_price=Decimal('150.00'),
            discount_percentage=10
        )
        
        # Test automatic calculations
        expected_discount = (Decimal('150.00') * 1 * 10) / 100
        expected_total = (Decimal('150.00') * 1) - expected_discount
        
        self.assertEqual(item.discount_amount, expected_discount)
        self.assertEqual(item.total_amount, expected_total)

    def test_payment_creation(self):
        """Test payment model creation."""
        invoice = Invoice.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            invoice_date=timezone.now(),
            total_amount=Decimal('150.00'),
            created_by=self.user
        )
        
        payment = Payment.objects.create(
            invoice=invoice,
            payment_method=self.payment_method,
            amount=Decimal('150.00'),
            payment_date=timezone.now(),
            created_by=self.user
        )
        
        self.assertEqual(payment.invoice, invoice)
        self.assertEqual(payment.amount, Decimal('150.00'))

    def test_refund_creation(self):
        """Test refund model creation."""
        invoice = Invoice.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            invoice_date=timezone.now(),
            total_amount=Decimal('150.00'),
            created_by=self.user
        )
        
        refund = Refund.objects.create(
            invoice=invoice,
            amount=Decimal('50.00'),
            reason_en='Patient request',
            reason_ar='طلب المريض',
            created_by=self.user
        )
        
        self.assertEqual(refund.invoice, invoice)
        self.assertEqual(refund.amount, Decimal('50.00'))
        self.assertEqual(refund.status, Refund.REFUND_STATUS.pending)

    def test_discount_creation(self):
        """Test discount model creation."""
        discount = Discount.objects.create(
            name_en='Test Discount',
            name_ar='خصم تجريبي',
            description_en='Test discount description',
            description_ar='وصف الخصم التجريبي',
            discount_type='percentage',
            value=Decimal('10.00'),
            is_active=True,
            valid_from=timezone.now(),
            created_by=self.user
        )
        
        self.assertEqual(discount.name_en, 'Test Discount')
        self.assertEqual(discount.discount_type, 'percentage')
        self.assertTrue(discount.is_valid)


class BillingAPITestCase(APITestCase):
    """Test cases for billing API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        self.patient = Patient.objects.create(
            patient_id='P001',
            first_name_en='Ahmed',
            first_name_ar='أحمد',
            last_name_en='Hassan',
            last_name_ar='حسن',
            phone='+966501234567',
            email='ahmed@example.com'
        )
        
        self.doctor = Doctor.objects.create(
            doctor_id='D001',
            first_name_en='Dr. Sarah',
            first_name_ar='د. سارة',
            last_name_en='Johnson',
            last_name_ar='جونسون',
            specialization_en='General Medicine',
            specialization_ar='الطب العام',
            license_number='MD123456'
        )
        
        self.category = ServiceCategory.objects.create(
            name_en='Consultations',
            name_ar='الاستشارات',
            description_en='Medical consultations',
            description_ar='الاستشارات الطبية'
        )
        
        self.service = Service.objects.create(
            service_id='S001',
            name_en='General Consultation',
            name_ar='استشارة عامة',
            description_en='General medical consultation',
            description_ar='استشارة طبية عامة',
            category=self.category,
            service_type='consultation',
            base_price=Decimal('150.00')
        )
        
        self.payment_method = PaymentMethod.objects.create(
            name_en='Cash',
            name_ar='نقداً',
            payment_type='cash',
            requires_reference=False
        )

    def test_patient_list_api(self):
        """Test patient list API endpoint."""
        url = '/api/patients/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_patient_create_api(self):
        """Test patient create API endpoint."""
        url = '/api/patients/'
        data = {
            'patient_id': 'P002',
            'first_name_en': 'Fatima',
            'first_name_ar': 'فاطمة',
            'last_name_en': 'Ali',
            'last_name_ar': 'علي',
            'phone': '+966501234568',
            'email': 'fatima@example.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 2)

    def test_invoice_create_api(self):
        """Test invoice create API endpoint."""
        url = '/api/invoices/'
        data = {
            'patient': str(self.patient.id),
            'doctor': str(self.doctor.id),
            'visit_reference': 'VISIT-001',
            'tax_rate': 15.0,
            'notes_en': 'Test invoice',
            'notes_ar': 'فاتورة تجريبية',
            'invoice_date': timezone.now().isoformat(),
            'items': [
                {
                    'service': str(self.service.id),
                    'description_en': 'Test consultation',
                    'description_ar': 'استشارة تجريبية',
                    'quantity': 1,
                    'unit_price': '150.00'
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Invoice.objects.count(), 1)

    def test_payment_create_api(self):
        """Test payment create API endpoint."""
        # First create an invoice
        invoice = Invoice.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            invoice_date=timezone.now(),
            total_amount=Decimal('150.00'),
            created_by=self.user
        )
        
        url = '/api/payments/'
        data = {
            'invoice': str(invoice.id),
            'payment_method': str(self.payment_method.id),
            'amount': '150.00',
            'payment_date': timezone.now().isoformat(),
            'notes_en': 'Test payment',
            'notes_ar': 'دفعة تجريبية'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)

    def test_discount_create_api(self):
        """Test discount create API endpoint."""
        url = '/api/discounts/'
        data = {
            'name_en': 'Test Discount',
            'name_ar': 'خصم تجريبي',
            'description_en': 'Test discount description',
            'description_ar': 'وصف الخصم التجريبي',
            'discount_type': 'percentage',
            'value': '10.00',
            'is_active': True,
            'valid_from': timezone.now().isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Discount.objects.count(), 1)

    def test_financial_summary_api(self):
        """Test financial summary API endpoint."""
        # Create some test data
        invoice = Invoice.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            invoice_date=timezone.now(),
            total_amount=Decimal('150.00'),
            paid_amount=Decimal('100.00'),
            outstanding_amount=Decimal('50.00'),
            created_by=self.user
        )
        
        url = '/api/reports/summary/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_invoices'], 1)
        self.assertEqual(response.data['total_revenue'], '150.00')

    def test_unauthorized_access(self):
        """Test that unauthorized access is denied."""
        self.client.credentials()  # Remove authentication
        url = '/api/patients/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
