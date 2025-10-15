"""
Filters for billing models.
"""

import django_filters
from django.db.models import Q
from django.db import models
from .models import Invoice, Payment, Refund, PaymentMethod


class InvoiceFilter(django_filters.FilterSet):
    """Filter for invoices."""
    status = django_filters.ChoiceFilter(choices=Invoice.INVOICE_STATUS)
    patient = django_filters.UUIDFilter(field_name='patient__id')
    doctor = django_filters.UUIDFilter(field_name='doctor__id')
    invoice_date_from = django_filters.DateTimeFilter(field_name='invoice_date', lookup_expr='gte')
    invoice_date_to = django_filters.DateTimeFilter(field_name='invoice_date', lookup_expr='lte')
    due_date_from = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='gte')
    due_date_to = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='lte')
    total_amount_min = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_max = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    outstanding_amount_min = django_filters.NumberFilter(field_name='outstanding_amount', lookup_expr='gte')
    outstanding_amount_max = django_filters.NumberFilter(field_name='outstanding_amount', lookup_expr='lte')
    is_overdue = django_filters.BooleanFilter(method='filter_overdue')
    is_fully_paid = django_filters.BooleanFilter(method='filter_fully_paid')
    
    class Meta:
        model = Invoice
        fields = [
            'status', 'patient', 'doctor', 'invoice_date_from', 'invoice_date_to',
            'due_date_from', 'due_date_to', 'total_amount_min', 'total_amount_max',
            'outstanding_amount_min', 'outstanding_amount_max', 'is_overdue', 'is_fully_paid'
        ]

    def filter_overdue(self, queryset, name, value):
        """Filter overdue invoices."""
        if value:
            from django.utils import timezone
            return queryset.filter(
                due_date__lt=timezone.now(),
                status__in=[Invoice.INVOICE_STATUS.pending, Invoice.INVOICE_STATUS.draft]
            )
        return queryset

    def filter_fully_paid(self, queryset, name, value):
        """Filter fully paid invoices."""
        if value:
            return queryset.filter(paid_amount__gte=models.F('total_amount'))
        return queryset


class PaymentFilter(django_filters.FilterSet):
    """Filter for payments."""
    payment_method = django_filters.UUIDFilter(field_name='payment_method__id')
    payment_type = django_filters.ChoiceFilter(field_name='payment_method__payment_type', choices=PaymentMethod.PAYMENT_TYPES)
    payment_date_from = django_filters.DateTimeFilter(field_name='payment_date', lookup_expr='gte')
    payment_date_to = django_filters.DateTimeFilter(field_name='payment_date', lookup_expr='lte')
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    is_verified = django_filters.BooleanFilter(field_name='is_verified')
    invoice = django_filters.UUIDFilter(field_name='invoice__id')
    created_by = django_filters.UUIDFilter(field_name='created_by__id')
    
    class Meta:
        model = Payment
        fields = [
            'payment_method', 'payment_type', 'payment_date_from', 'payment_date_to',
            'amount_min', 'amount_max', 'is_verified', 'invoice', 'created_by'
        ]


class RefundFilter(django_filters.FilterSet):
    """Filter for refunds."""
    status = django_filters.ChoiceFilter(choices=Refund.REFUND_STATUS)
    invoice = django_filters.UUIDFilter(field_name='invoice__id')
    created_from = django_filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created', lookup_expr='lte')
    processed_from = django_filters.DateTimeFilter(field_name='processed_date', lookup_expr='gte')
    processed_to = django_filters.DateTimeFilter(field_name='processed_date', lookup_expr='lte')
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    created_by = django_filters.UUIDFilter(field_name='created_by__id')
    processed_by = django_filters.UUIDFilter(field_name='processed_by__id')
    
    class Meta:
        model = Refund
        fields = [
            'status', 'invoice', 'created_from', 'created_to', 'processed_from',
            'processed_to', 'amount_min', 'amount_max', 'created_by', 'processed_by'
        ]
