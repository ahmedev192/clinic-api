from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Sample, SampleCollection


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = [
        'barcode', 'tracking_code', 'request_item', 'sample_type', 
        'status', 'collection_date', 'collector_name', 'created_at'
    ]
    list_filter = [
        'status', 'sample_type', 'collection_date', 'created_at', 'created_by'
    ]
    search_fields = [
        'barcode', 'tracking_code', 'collector_name', 'collector_name_ar',
        'collection_notes_en', 'collection_notes_ar'
    ]
    ordering = ['-created_at']
    readonly_fields = ['barcode', 'tracking_code', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Sample Identification'), {
            'fields': ('barcode', 'tracking_code', 'request_item')
        }),
        (_('Sample Details'), {
            'fields': ('sample_type', 'volume', 'container_type')
        }),
        (_('Collection Information'), {
            'fields': ('collection_date', 'collector_name', 'collector_name_ar', 'collection_location')
        }),
        (_('Status and Storage'), {
            'fields': ('status', 'storage_location', 'temperature', 'expiry_date')
        }),
        (_('Notes'), {
            'fields': ('collection_notes_en', 'collection_notes_ar', 'rejection_reason_en', 'rejection_reason_ar')
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


@admin.register(SampleCollection)
class SampleCollectionAdmin(admin.ModelAdmin):
    list_display = [
        'collection_batch_id', 'collection_date', 'collector_name', 
        'total_samples', 'collected_samples', 'created_at'
    ]
    list_filter = ['collection_date', 'created_at', 'created_by']
    search_fields = [
        'collection_batch_id', 'collector_name', 'collector_name_ar',
        'location', 'notes_en', 'notes_ar'
    ]
    ordering = ['-collection_date']
    readonly_fields = ['collection_batch_id', 'created_at', 'updated_at']
