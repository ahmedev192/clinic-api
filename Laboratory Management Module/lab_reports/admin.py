from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import LabReport, ReportTemplate, ReportDelivery


@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    list_display = [
        'report_number', 'lab_request', 'title_en', 'format', 'status', 
        'is_public', 'generated_at', 'created_at'
    ]
    list_filter = ['status', 'format', 'is_public', 'generated_at', 'created_at', 'created_by']
    search_fields = [
        'report_number', 'title_en', 'title_ar', 'lab_request__request_number',
        'lab_request__patient_name', 'lab_request__patient_name_ar'
    ]
    ordering = ['-created_at']
    readonly_fields = ['report_number', 'file_size', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Report Information'), {
            'fields': ('report_number', 'lab_request', 'title_en', 'title_ar', 'format')
        }),
        (_('Content'), {
            'fields': ('content_en', 'content_ar'),
            'classes': ('collapse',)
        }),
        (_('File Information'), {
            'fields': ('file_path', 'file_size'),
            'classes': ('collapse',)
        }),
        (_('Status and Access'), {
            'fields': ('status', 'is_public')
        }),
        (_('Timestamps'), {
            'fields': ('generated_at', 'delivered_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name_en', 'name_ar', 'is_default', 'is_active', 'created_at'
    ]
    list_filter = ['is_default', 'is_active', 'created_at', 'created_by']
    search_fields = ['name_en', 'name_ar', 'description_en', 'description_ar']
    ordering = ['name_en']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Template Information'), {
            'fields': ('name_en', 'name_ar', 'description_en', 'description_ar')
        }),
        (_('Template Content'), {
            'fields': ('template_content_en', 'template_content_ar'),
            'classes': ('collapse',)
        }),
        (_('Settings'), {
            'fields': ('is_default', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReportDelivery)
class ReportDeliveryAdmin(admin.ModelAdmin):
    list_display = [
        'report', 'recipient_name', 'delivery_method', 'status', 
        'sent_at', 'delivered_at', 'created_at'
    ]
    list_filter = [
        'delivery_method', 'status', 'sent_at', 'delivered_at', 'created_at'
    ]
    search_fields = [
        'report__report_number', 'recipient_name', 'recipient_name_ar',
        'recipient_email', 'recipient_phone', 'delivery_reference'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (_('Delivery Information'), {
            'fields': ('report', 'delivery_method', 'delivery_reference')
        }),
        (_('Recipient Information'), {
            'fields': ('recipient_name', 'recipient_name_ar', 'recipient_email', 'recipient_phone')
        }),
        (_('Status'), {
            'fields': ('status', 'sent_at', 'delivered_at', 'opened_at')
        }),
        (_('Error Handling'), {
            'fields': ('error_message', 'retry_count'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
