"""
Serializers for billing models.
"""

from rest_framework import serializers
from apps.accounts.models import User
from .models import (
    Patient, Doctor, ServiceCategory, Service, Invoice, InvoiceItem,
    PaymentMethod, Payment, Refund, Discount, AuditLog
)


class PatientSerializer(serializers.ModelSerializer):
    full_name_en = serializers.ReadOnlyField()
    full_name_ar = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = [
            'id', 'patient_code', 'first_name_en', 'first_name_ar',
            'last_name_en', 'last_name_ar', 'full_name_en', 'full_name_ar',
            'phone_number', 'email', 'date_of_birth', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DoctorSerializer(serializers.ModelSerializer):
    full_name_en = serializers.ReadOnlyField()
    full_name_ar = serializers.ReadOnlyField()

    class Meta:
        model = Doctor
        fields = [
            'id', 'doctor_id', 'first_name_en', 'first_name_ar',
            'last_name_en', 'last_name_ar', 'full_name_en', 'full_name_ar',
            'specialization_en', 'specialization_ar', 'license_number',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = [
            'id', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ServiceSerializer(serializers.ModelSerializer):
    category_name_en = serializers.CharField(source='category.name_en', read_only=True)
    category_name_ar = serializers.CharField(source='category.name_ar', read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'service_id', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'category', 'category_name_en', 'category_name_ar', 'service_type',
            'base_price', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceItemSerializer(serializers.ModelSerializer):
    service_name_en = serializers.CharField(source='service.name_en', read_only=True)
    service_name_ar = serializers.CharField(source='service.name_ar', read_only=True)
    service_type = serializers.CharField(source='service.service_type', read_only=True)

    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'service', 'service_name_en', 'service_name_ar', 'service_type',
            'description_en', 'description_ar', 'quantity', 'unit_price',
            'discount_percentage', 'discount_amount', 'total_amount',
            'service_reference', 'notes_en', 'notes_ar', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']


class InvoiceItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = [
            'service', 'description_en', 'description_ar', 'quantity', 'unit_price',
            'discount_percentage', 'service_reference', 'notes_en', 'notes_ar'
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    patient_name_en = serializers.CharField(source='patient.full_name_en', read_only=True)
    patient_name_ar = serializers.CharField(source='patient.full_name_ar', read_only=True)
    doctor_name_en = serializers.CharField(source='doctor.full_name_en', read_only=True)
    doctor_name_ar = serializers.CharField(source='doctor.full_name_ar', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    is_fully_paid = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'patient', 'patient_name_en', 'patient_name_ar',
            'doctor', 'doctor_name_en', 'doctor_name_ar', 'visit_reference',
            'service_reference', 'subtotal', 'tax_rate', 'tax_amount',
            'discount_amount', 'total_amount', 'paid_amount', 'outstanding_amount',
            'status', 'notes_en', 'notes_ar', 'invoice_date', 'due_date',
            'is_fully_paid', 'is_overdue', 'items', 'created_by', 'created_by_username',
            'updated_by', 'updated_by_username', 'created', 'modified'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'subtotal', 'tax_amount', 'total_amount',
            'paid_amount', 'outstanding_amount', 'is_fully_paid', 'is_overdue',
            'created', 'modified'
        ]


class InvoiceCreateSerializer(serializers.ModelSerializer):
    items = InvoiceItemCreateSerializer(many=True)

    class Meta:
        model = Invoice
        fields = [
            'patient', 'doctor', 'visit_reference', 'service_reference',
            'tax_rate', 'discount_amount', 'notes_en', 'notes_ar',
            'invoice_date', 'due_date', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)
        
        # Generate invoice number
        invoice.invoice_number = f"INV-{invoice.id.hex[:8].upper()}"
        
        # Create invoice items
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        # Calculate totals
        invoice.calculate_totals()
        invoice.save()
        
        return invoice


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name_en', 'name_ar', 'payment_type', 'is_active',
            'requires_reference', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    payment_method_name_en = serializers.CharField(source='payment_method.name_en', read_only=True)
    payment_method_name_ar = serializers.CharField(source='payment_method.name_ar', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    verified_by_username = serializers.CharField(source='verified_by.username', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_number', 'payment_method', 'payment_method_name_en',
            'payment_method_name_ar', 'amount', 'reference_number', 'payment_date',
            'notes_en', 'notes_ar', 'is_verified', 'verified_by', 'verified_by_username',
            'verified_at', 'created_by', 'created_by_username', 'updated_by',
            'updated_by_username', 'created', 'modified'
        ]
        read_only_fields = [
            'id', 'verified_at', 'created', 'modified'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'invoice', 'payment_method', 'amount', 'reference_number',
            'payment_date', 'notes_en', 'notes_ar'
        ]

    def create(self, validated_data):
        payment = Payment.objects.create(**validated_data)
        # Update invoice paid amount
        payment.invoice.update_paid_amount()
        return payment


class RefundSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    processed_by_username = serializers.CharField(source='processed_by.username', read_only=True)

    class Meta:
        model = Refund
        fields = [
            'id', 'invoice', 'invoice_number', 'refund_number', 'amount',
            'reason_en', 'reason_ar', 'notes_en', 'notes_ar', 'status',
            'processed_date', 'processed_by', 'processed_by_username',
            'created_by', 'created_by_username', 'updated_by',
            'updated_by_username', 'created', 'modified'
        ]
        read_only_fields = [
            'id', 'refund_number', 'created', 'modified'
        ]


class RefundCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = [
            'invoice', 'amount', 'reason_en', 'reason_ar', 'notes_en', 'notes_ar'
        ]


class DiscountSerializer(serializers.ModelSerializer):
    is_valid = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Discount
        fields = [
            'id', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'discount_type', 'value', 'max_discount_amount', 'min_invoice_amount',
            'is_active', 'valid_from', 'valid_until', 'usage_limit', 'used_count',
            'code', 'is_valid', 'created_by', 'created_by_username', 'created_at'
        ]
        read_only_fields = ['id', 'used_count', 'created_at']


class DiscountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = [
            'name_en', 'name_ar', 'description_en', 'description_ar',
            'discount_type', 'value', 'max_discount_amount', 'min_invoice_amount',
            'is_active', 'valid_from', 'valid_until', 'usage_limit', 'code'
        ]


class AuditLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    payment_amount = serializers.DecimalField(source='payment.amount', max_digits=10, decimal_places=2, read_only=True)
    refund_number = serializers.CharField(source='refund.refund_number', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'action_type', 'user', 'user_username', 'timestamp',
            'invoice', 'invoice_number', 'payment', 'payment_amount',
            'refund', 'refund_number', 'discount', 'description_en',
            'description_ar', 'old_values', 'new_values', 'ip_address', 'user_agent'
        ]
        read_only_fields = ['id', 'timestamp']


class FinancialSummarySerializer(serializers.Serializer):
    """Serializer for financial summary reports."""
    total_invoices = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_outstanding = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_refunds = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_discounts = serializers.DecimalField(max_digits=12, decimal_places=2)
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()


class PaymentHistorySerializer(serializers.Serializer):
    """Serializer for patient payment history."""
    invoice_number = serializers.CharField()
    invoice_date = serializers.DateTimeField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    outstanding_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    payments = PaymentSerializer(many=True)
    refunds = RefundSerializer(many=True)

