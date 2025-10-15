"""
Django admin configuration for the Consultation & Clinical Notes Module.
Provides comprehensive admin interface for data management.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Consultation, Diagnosis, ConsultationDiagnosis, Prescription, PrescriptionItem,
    LabOrder, LabResult, Attachment, FollowUpNote, AuditLog
)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    """Admin interface for Consultation model."""
    
    list_display = [
        'consultation_code', 'patient', 'doctor', 'consultation_type',
        'status', 'consultation_date', 'duration_minutes', 'created_by'
    ]
    list_filter = [
        'consultation_type', 'status', 'consultation_date', 'created_by'
    ]
    search_fields = [
        'consultation_code', 'patient', 'doctor', 'chief_complaint_en',
        'chief_complaint_ar', 'symptoms_en', 'symptoms_ar'
    ]
    readonly_fields = ['id', 'consultation_code', 'created', 'modified']
    date_hierarchy = 'consultation_date'
    ordering = ['-consultation_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 'consultation_code', 'patient', 'doctor', 'appointment',
                'consultation_type', 'status'
            )
        }),
        ('Clinical Information (English)', {
            'fields': (
                'chief_complaint_en', 'symptoms_en', 'examination_findings_en',
                'assessment_notes_en'
            )
        }),
        ('Clinical Information (Arabic)', {
            'fields': (
                'chief_complaint_ar', 'symptoms_ar', 'examination_findings_ar',
                'assessment_notes_ar'
            )
        }),
        ('Timing', {
            'fields': ('consultation_date', 'duration_minutes')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by', 'created', 'modified')
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('created_by', 'updated_by')


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    """Admin interface for Diagnosis model."""
    
    list_display = [
        'diagnosis_code', 'name_en', 'name_ar', 'category', 'severity_level',
        'is_chronic', 'is_contagious'
    ]
    list_filter = ['category', 'severity_level', 'is_chronic', 'is_contagious']
    search_fields = [
        'diagnosis_code', 'name_en', 'name_ar', 'category', 'description_en',
        'description_ar'
    ]
    readonly_fields = ['id', 'created', 'modified']
    ordering = ['name_en']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'diagnosis_code', 'category')
        }),
        ('Diagnosis Details (English)', {
            'fields': ('name_en', 'description_en')
        }),
        ('Diagnosis Details (Arabic)', {
            'fields': ('name_ar', 'description_ar')
        }),
        ('Clinical Properties', {
            'fields': ('is_chronic', 'is_contagious', 'severity_level')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified')
        })
    )


class ConsultationDiagnosisInline(admin.TabularInline):
    """Inline admin for ConsultationDiagnosis."""
    model = ConsultationDiagnosis
    extra = 0
    fields = ['diagnosis', 'status', 'notes_en', 'is_resolved']


class PrescriptionItemInline(admin.TabularInline):
    """Inline admin for PrescriptionItem."""
    model = PrescriptionItem
    extra = 0
    fields = [
        'medication_name_en', 'medication_name_ar', 'dosage', 'frequency',
        'quantity', 'duration_days'
    ]


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    """Admin interface for Prescription model."""
    
    list_display = [
        'prescription_code', 'consultation', 'status', 'pharmacy_status',
        'prescribed_date', 'valid_until'
    ]
    list_filter = ['status', 'pharmacy_status', 'prescribed_date']
    search_fields = [
        'prescription_code', 'notes_en', 'notes_ar', 'pharmacy_notes'
    ]
    readonly_fields = ['id', 'prescription_code', 'created', 'modified']
    inlines = [PrescriptionItemInline]
    date_hierarchy = 'prescribed_date'
    ordering = ['-prescribed_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'prescription_code', 'consultation', 'status')
        }),
        ('Prescription Details (English)', {
            'fields': ('notes_en',)
        }),
        ('Prescription Details (Arabic)', {
            'fields': ('notes_ar',)
        }),
        ('Validity', {
            'fields': ('prescribed_date', 'valid_until')
        }),
        ('Pharmacy Integration', {
            'fields': ('pharmacy_status', 'pharmacy_notes')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified')
        })
    )


class LabResultInline(admin.TabularInline):
    """Inline admin for LabResult."""
    model = LabResult
    extra = 0
    fields = [
        'result_value', 'reference_range', 'unit', 'status',
        'interpretation_en', 'result_date'
    ]


@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    """Admin interface for LabOrder model."""
    
    list_display = [
        'order_code', 'consultation', 'test_name_en', 'test_category',
        'priority', 'status', 'lab_status', 'ordered_date'
    ]
    list_filter = [
        'test_category', 'priority', 'status', 'lab_status', 'ordered_date'
    ]
    search_fields = [
        'order_code', 'test_name_en', 'test_name_ar', 'test_category',
        'clinical_justification_en', 'clinical_justification_ar'
    ]
    readonly_fields = ['id', 'order_code', 'created', 'modified']
    inlines = [LabResultInline]
    date_hierarchy = 'ordered_date'
    ordering = ['-ordered_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'order_code', 'consultation', 'test_category')
        }),
        ('Test Details (English)', {
            'fields': ('test_name_en', 'clinical_justification_en')
        }),
        ('Test Details (Arabic)', {
            'fields': ('test_name_ar', 'clinical_justification_ar')
        }),
        ('Order Details', {
            'fields': ('priority', 'status', 'ordered_date', 'requested_date')
        }),
        ('Laboratory Integration', {
            'fields': ('lab_reference', 'lab_status')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified')
        })
    )


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """Admin interface for Attachment model."""
    
    list_display = [
        'title_en', 'consultation', 'file_type', 'file_size',
        'is_confidential', 'uploaded_by', 'created'
    ]
    list_filter = [
        'file_type', 'is_confidential', 'access_level', 'created'
    ]
    search_fields = [
        'title_en', 'title_ar', 'file_name', 'description_en', 'description_ar'
    ]
    readonly_fields = ['id', 'file_size', 'created', 'modified']
    date_hierarchy = 'created'
    ordering = ['-created']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'consultation', 'file', 'file_name', 'file_type', 'file_size')
        }),
        ('File Details (English)', {
            'fields': ('title_en', 'description_en')
        }),
        ('File Details (Arabic)', {
            'fields': ('title_ar', 'description_ar')
        }),
        ('Security', {
            'fields': ('is_confidential', 'access_level')
        }),
        ('Upload Information', {
            'fields': ('uploaded_by', 'created', 'modified')
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('consultation', 'uploaded_by')


@admin.register(FollowUpNote)
class FollowUpNoteAdmin(admin.ModelAdmin):
    """Admin interface for FollowUpNote model."""
    
    list_display = [
        'consultation', 'note_type', 'is_urgent', 'note_date',
        'created_by', 'linked_appointment_id'
    ]
    list_filter = [
        'note_type', 'is_urgent', 'note_date', 'created_by'
    ]
    search_fields = [
        'content_en', 'content_ar', 'linked_appointment_id'
    ]
    readonly_fields = ['id', 'created', 'modified']
    date_hierarchy = 'note_date'
    ordering = ['-note_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'consultation', 'note_type', 'is_urgent')
        }),
        ('Note Content (English)', {
            'fields': ('content_en',)
        }),
        ('Note Content (Arabic)', {
            'fields': ('content_ar',)
        }),
        ('Timing', {
            'fields': ('note_date', 'linked_appointment_id')
        }),
        ('Author Information', {
            'fields': ('created_by', 'created', 'modified')
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('consultation', 'created_by')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model (read-only)."""
    
    list_display = [
        'user', 'action', 'model_name', 'object_id', 'ip_address', 'created'
    ]
    list_filter = ['action', 'model_name', 'created', 'user']
    search_fields = ['user__username', 'model_name', 'object_id', 'ip_address']
    readonly_fields = [
        'user', 'action', 'model_name', 'object_id', 'old_values',
        'new_values', 'ip_address', 'user_agent', 'created'
    ]
    date_hierarchy = 'created'
    ordering = ['-created']
    
    def has_add_permission(self, request):
        """Disable adding new audit logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing audit logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting audit logs."""
        return False
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user')


# Customize admin site
admin.site.site_header = "Clinic Management System - Consultation Module"
admin.site.site_title = "Consultation Admin"
admin.site.index_title = "Consultation & Clinical Notes Management"
