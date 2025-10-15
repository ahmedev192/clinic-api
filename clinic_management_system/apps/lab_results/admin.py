from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import LabResult, ResultAttachment


class ResultAttachmentInline(admin.TabularInline):
    model = ResultAttachment
    extra = 0
    fields = ['file', 'file_name', 'file_type', 'description_en', 'description_ar']
    readonly_fields = ['file_size', 'uploaded_at']


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = [
        'sample', 'measured_value', 'unit', 'abnormality_flag', 'status', 
        'is_approved', 'is_critical', 'created_at'
    ]
    list_filter = [
        'status', 'abnormality_flag', 'is_approved', 'is_critical', 
        'created_at', 'created_by', 'approved_by'
    ]
    search_fields = [
        'sample__barcode', 'sample__tracking_code', 'comments_en', 'comments_ar',
        'interpretation_en', 'interpretation_ar'
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'abnormality_flag', 'is_critical', 'created_at', 'updated_at', 
        'completed_at', 'approved_at', 'rejected_at'
    ]
    inlines = [ResultAttachmentInline]
    
    fieldsets = (
        (_('Sample Information'), {
            'fields': ('sample',)
        }),
        (_('Result Values'), {
            'fields': ('measured_value', 'unit', 'normal_range_min', 'normal_range_max', 'normal_range_text_en', 'normal_range_text_ar')
        }),
        (_('Interpretation'), {
            'fields': ('abnormality_flag', 'is_critical', 'comments_en', 'comments_ar', 'interpretation_en', 'interpretation_ar')
        }),
        (_('Status and Approval'), {
            'fields': ('status', 'is_approved', 'approved_by', 'approved_at')
        }),
        (_('Rejection'), {
            'fields': ('rejection_reason_en', 'rejection_reason_ar', 'rejected_by', 'rejected_at'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ResultAttachment)
class ResultAttachmentAdmin(admin.ModelAdmin):
    list_display = [
        'result', 'file_name', 'file_type', 'file_size', 'uploaded_at', 'uploaded_by'
    ]
    list_filter = ['file_type', 'uploaded_at', 'uploaded_by']
    search_fields = ['file_name', 'description_en', 'description_ar']
    ordering = ['-uploaded_at']
    readonly_fields = ['file_size', 'uploaded_at']
