from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import LabRequest, LabRequestItem


class LabRequestItemInline(admin.TabularInline):
    model = LabRequestItem
    extra = 0
    fields = ['test', 'quantity', 'notes_en', 'notes_ar', 'is_collected', 'is_completed']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LabRequest)
class LabRequestAdmin(admin.ModelAdmin):
    list_display = [
        'request_number', 'patient_name', 'doctor_name', 'status', 
        'urgency', 'request_date', 'created_by'
    ]
    list_filter = ['status', 'urgency', 'request_date', 'created_by']
    search_fields = [
        'request_number', 'patient_name', 'patient_name_ar', 
        'doctor_name', 'doctor_name_ar', 'clinical_notes_en', 'clinical_notes_ar'
    ]
    ordering = ['-request_date']
    readonly_fields = ['request_number', 'request_date', 'updated_at']
    inlines = [LabRequestItemInline]
    
    fieldsets = (
        (_('Request Information'), {
            'fields': ('request_number', 'status', 'urgency', 'request_date')
        }),
        (_('Patient Information'), {
            'fields': ('patient_id', 'patient_name', 'patient_name_ar')
        }),
        (_('Doctor Information'), {
            'fields': ('doctor_id', 'doctor_name', 'doctor_name_ar')
        }),
        (_('Clinical Information'), {
            'fields': ('clinical_notes_en', 'clinical_notes_ar', 'diagnosis_en', 'diagnosis_ar')
        }),
        (_('Timestamps'), {
            'fields': ('collection_date', 'completion_date', 'updated_at'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )


@admin.register(LabRequestItem)
class LabRequestItemAdmin(admin.ModelAdmin):
    list_display = [
        'request', 'test', 'quantity', 'is_collected', 'is_completed', 
        'total_price', 'created_at'
    ]
    list_filter = ['is_collected', 'is_completed', 'test__category', 'created_at']
    search_fields = [
        'request__request_number', 'test__name_en', 'test__name_ar',
        'notes_en', 'notes_ar'
    ]
    ordering = ['-created_at']
    readonly_fields = ['total_price', 'created_at', 'updated_at']
