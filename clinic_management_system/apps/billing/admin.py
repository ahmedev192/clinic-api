"""
Admin configuration for billing models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    ServiceCategory, Service, Invoice, InvoiceItem,
    PaymentMethod, Payment, Refund, Discount, AuditLog
)
from apps.patient_management.models import Patient
from apps.staff_management.models import Doctor


# Patient and Doctor admin registrations moved to their respective modules


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name_en', 'name_ar']
    readonly_fields = ['created_at']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['service_id', 'name_en', 'name_ar', 'category', 'service_type', 'base_price', 'is_active']
    list_filter = ['category', 'service_type', 'is_active', 'created_at']
    search_fields = ['service_id', 'name_en', 'name_ar', 'description_en', 'description_ar']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['name_en']


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ['total_amount']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'patient_link', 'doctor_link', 'status', 'total_amount',
        'paid_amount', 'outstanding_amount', 'invoice_date', 'is_overdue'
    ]
    list_filter = ['status', 'invoice_date', 'created']
    search_fields = ['invoice_number', 'patient__first_name_en', 'patient__last_name_en', 'doctor__first_name_en']
    readonly_fields = [
        'id', 'invoice_number', 'subtotal', 'tax_amount', 'total_amount',
        'paid_amount', 'outstanding_amount', 'created', 'modified'
    ]
    inlines = [InvoiceItemInline]
    date_hierarchy = 'invoice_date'
    ordering = ['-created', '-invoice_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('invoice_number', 'patient', 'doctor', 'visit_reference', 'service_reference')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount_amount', 'total_amount', 'paid_amount', 'outstanding_amount')
        }),
        ('Status & Dates', {
            'fields': ('status', 'invoice_date', 'due_date')
        }),
        ('Notes', {
            'fields': ('notes_en', 'notes_ar')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by', 'created', 'modified'),
            'classes': ('collapse',)
        }),
    )

    def patient_link(self, obj):
        if obj.patient:
            url = reverse('admin:billing_patient_change', args=[obj.patient.id])
            return format_html('<a href="{}">{}</a>', url, obj.patient.full_name_en)
        return '-'
    patient_link.short_description = 'Patient'

    def doctor_link(self, obj):
        if obj.doctor:
            url = reverse('admin:billing_doctor_change', args=[obj.doctor.id])
            return format_html('<a href="{}">{}</a>', url, obj.doctor.full_name_en)
        return '-'
    doctor_link.short_description = 'Doctor'

    def is_overdue(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">Yes</span>')
        return 'No'
    is_overdue.short_description = 'Overdue'
    is_overdue.boolean = True


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'service', 'description_en', 'quantity', 'unit_price', 'total_amount']
    list_filter = ['service__category', 'service__service_type', 'created_at']
    search_fields = ['invoice__invoice_number', 'service__name_en', 'description_en']
    readonly_fields = ['id', 'total_amount', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'payment_type', 'is_active', 'requires_reference']
    list_filter = ['payment_type', 'is_active']
    search_fields = ['name_en', 'name_ar']
    readonly_fields = ['created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_link', 'payment_method', 'amount', 'reference_number',
        'payment_date', 'is_verified', 'created_by'
    ]
    list_filter = ['payment_method', 'is_verified', 'payment_date', 'created']
    search_fields = ['invoice__invoice_number', 'reference_number', 'notes_en']
    readonly_fields = ['id', 'created', 'modified']
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date', '-created']

    def invoice_link(self, obj):
        if obj.invoice:
            url = reverse('admin:billing_invoice_change', args=[obj.invoice.id])
            return format_html('<a href="{}">{}</a>', url, obj.invoice.invoice_number)
        return '-'
    invoice_link.short_description = 'Invoice'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = [
        'refund_number', 'invoice_link', 'amount', 'status', 'reason_en',
        'processed_date', 'created_by'
    ]
    list_filter = ['status', 'created', 'processed_date']
    search_fields = ['refund_number', 'invoice__invoice_number', 'reason_en', 'reason_ar']
    readonly_fields = ['id', 'refund_number', 'created', 'modified']
    date_hierarchy = 'created'
    ordering = ['-created']

    def invoice_link(self, obj):
        if obj.invoice:
            url = reverse('admin:billing_invoice_change', args=[obj.invoice.id])
            return format_html('<a href="{}">{}</a>', url, obj.invoice.invoice_number)
        return '-'
    invoice_link.short_description = 'Invoice'


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = [
        'name_en', 'name_ar', 'discount_type', 'value', 'is_active',
        'valid_from', 'valid_until', 'used_count', 'usage_limit'
    ]
    list_filter = ['discount_type', 'is_active', 'valid_from', 'created_at']
    search_fields = ['name_en', 'name_ar', 'code', 'description_en']
    readonly_fields = ['id', 'used_count', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'user', 'timestamp', 'invoice_link', 'payment_link', 'refund_link']
    list_filter = ['action_type', 'timestamp', 'user']
    search_fields = ['description_en', 'description_ar', 'user__username']
    readonly_fields = ['id', 'timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    def invoice_link(self, obj):
        if obj.invoice:
            url = reverse('admin:billing_invoice_change', args=[obj.invoice.id])
            return format_html('<a href="{}">{}</a>', url, obj.invoice.invoice_number)
        return '-'
    invoice_link.short_description = 'Invoice'

    def payment_link(self, obj):
        if obj.payment:
            return format_html('<a href="{}">{}</a>', 
                reverse('admin:billing_payment_change', args=[obj.payment.id]),
                str(obj.payment.amount)
            )
        return '-'
    payment_link.short_description = 'Payment'

    def refund_link(self, obj):
        if obj.refund:
            return format_html('<a href="{}">{}</a>', 
                reverse('admin:billing_refund_change', args=[obj.refund.id]),
                obj.refund.refund_number
            )
        return '-'
    refund_link.short_description = 'Refund'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
