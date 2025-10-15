"""
Django Admin configuration for Patient Management models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Patient, MedicalHistory, Allergy, ChronicCondition, 
    PatientDocument, PatientSearchLog
)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin interface for Patient model"""
    
    list_display = [
        'patient_code', 'get_full_name', 'get_full_name_ar', 'gender', 
        'get_age', 'phone_number', 'email', 'status', 'created_at'
    ]
    list_filter = [
        'gender', 'status', 'blood_type', 'country', 'city', 
        'created_at', 'is_deleted'
    ]
    search_fields = [
        'patient_code', 'first_name_en', 'first_name_ar', 'last_name_en', 
        'last_name_ar', 'national_id', 'phone_number', 'email'
    ]
    readonly_fields = [
        'patient_code', 'created_at', 'updated_at', 'created_by', 
        'updated_by', 'is_deleted', 'deleted_at', 'deleted_by'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'patient_code', 'first_name_en', 'first_name_ar',
                'last_name_en', 'last_name_ar', 'middle_name_en', 'middle_name_ar',
                'gender', 'date_of_birth'
            )
        }),
        ('Contact Information', {
            'fields': (
                'phone_number', 'secondary_phone', 'email',
                'address_en', 'address_ar', 'city', 'state_province',
                'postal_code', 'country'
            )
        }),
        ('Identification', {
            'fields': ('national_id', 'passport_number', 'blood_type')
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name', 'emergency_contact_phone',
                'emergency_contact_relationship'
            )
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('Metadata', {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by',
                'is_deleted', 'deleted_at', 'deleted_by'
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_full_name(self, obj):
        """Display full name in English"""
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name (EN)'
    
    def get_full_name_ar(self, obj):
        """Display full name in Arabic"""
        return obj.get_full_name_ar()
    get_full_name_ar.short_description = 'Full Name (AR)'
    
    def get_age(self, obj):
        """Display patient's age"""
        return obj.get_age()
    get_age.short_description = 'Age'
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields"""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['soft_delete_patients', 'activate_patients', 'deactivate_patients']
    
    def soft_delete_patients(self, request, queryset):
        """Soft delete selected patients"""
        count = 0
        for patient in queryset:
            if not patient.is_deleted:
                patient.soft_delete(request.user)
                count += 1
        self.message_user(request, f'{count} patients were soft deleted.')
    soft_delete_patients.short_description = 'Soft delete selected patients'
    
    def activate_patients(self, request, queryset):
        """Activate selected patients"""
        count = queryset.filter(status='inactive').update(status='active')
        self.message_user(request, f'{count} patients were activated.')
    activate_patients.short_description = 'Activate selected patients'
    
    def deactivate_patients(self, request, queryset):
        """Deactivate selected patients"""
        count = queryset.filter(status='active').update(status='inactive')
        self.message_user(request, f'{count} patients were deactivated.')
    deactivate_patients.short_description = 'Deactivate selected patients'


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    """Admin interface for MedicalHistory model"""
    
    list_display = [
        'patient_link', 'title_en', 'category', 'event_date', 'created_at'
    ]
    list_filter = ['category', 'event_date', 'created_at']
    search_fields = [
        'patient__patient_code', 'title_en', 'title_ar', 
        'description_en', 'description_ar', 'diagnosis_code'
    ]
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    def patient_link(self, obj):
        """Link to patient detail page"""
        url = reverse('admin:patient_management_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient.patient_code)
    patient_link.short_description = 'Patient'
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields"""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    """Admin interface for Allergy model"""
    
    list_display = [
        'patient_link', 'allergen_en', 'allergy_type', 'severity', 'created_at'
    ]
    list_filter = ['allergy_type', 'severity', 'created_at']
    search_fields = [
        'patient__patient_code', 'allergen_en', 'allergen_ar',
        'description_en', 'description_ar', 'symptoms'
    ]
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    def patient_link(self, obj):
        """Link to patient detail page"""
        url = reverse('admin:patient_management_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient.patient_code)
    patient_link.short_description = 'Patient'
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields"""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ChronicCondition)
class ChronicConditionAdmin(admin.ModelAdmin):
    """Admin interface for ChronicCondition model"""
    
    list_display = [
        'patient_link', 'condition_name_en', 'condition_type', 
        'severity', 'is_active', 'diagnosis_date'
    ]
    list_filter = ['condition_type', 'severity', 'is_active', 'diagnosis_date']
    search_fields = [
        'patient__patient_code', 'condition_name_en', 'condition_name_ar',
        'description_en', 'description_ar', 'icd_code'
    ]
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    def patient_link(self, obj):
        """Link to patient detail page"""
        url = reverse('admin:patient_management_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient.patient_code)
    patient_link.short_description = 'Patient'
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by fields"""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    """Admin interface for PatientDocument model"""
    
    list_display = [
        'patient_link', 'title_en', 'document_type', 'file_size_display',
        'is_verified', 'upload_date'
    ]
    list_filter = ['document_type', 'is_verified', 'upload_date']
    search_fields = [
        'patient__patient_code', 'title_en', 'title_ar',
        'description_en', 'description_ar'
    ]
    readonly_fields = [
        'file_size', 'file_extension', 'upload_date', 'uploaded_by',
        'verified_by', 'verified_at'
    ]
    
    def patient_link(self, obj):
        """Link to patient detail page"""
        url = reverse('admin:patient_management_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient.patient_code)
    patient_link.short_description = 'Patient'
    
    def file_size_display(self, obj):
        """Display human-readable file size"""
        return obj.get_file_size_display()
    file_size_display.short_description = 'File Size'
    
    def save_model(self, request, obj, form, change):
        """Set uploaded_by field"""
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['verify_documents', 'unverify_documents']
    
    def verify_documents(self, request, queryset):
        """Verify selected documents"""
        count = queryset.filter(is_verified=False).update(
            is_verified=True,
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{count} documents were verified.')
    verify_documents.short_description = 'Verify selected documents'
    
    def unverify_documents(self, request, queryset):
        """Unverify selected documents"""
        count = queryset.filter(is_verified=True).update(
            is_verified=False,
            verified_by=None,
            verified_at=None
        )
        self.message_user(request, f'{count} documents were unverified.')
    unverify_documents.short_description = 'Unverify selected documents'


@admin.register(PatientSearchLog)
class PatientSearchLogAdmin(admin.ModelAdmin):
    """Admin interface for PatientSearchLog model"""
    
    list_display = [
        'searcher', 'search_query', 'results_count', 'search_timestamp'
    ]
    list_filter = ['search_timestamp', 'searcher']
    search_fields = ['searcher__username', 'search_query']
    readonly_fields = ['searcher', 'search_query', 'search_filters', 'results_count', 'search_timestamp']
    
    def has_add_permission(self, request):
        """Disable adding search logs through admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable changing search logs through admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting search logs"""
        return True
