from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import TestCategory, LabTest


@admin.register(TestCategory)
class TestCategoryAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name_en', 'name_ar', 'description_en', 'description_ar']
    ordering = ['name_en']


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'category', 'code', 'price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at', 'sample_type']
    search_fields = ['name_en', 'name_ar', 'code', 'description_en', 'description_ar']
    ordering = ['category', 'name_en']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name_en', 'name_ar', 'code', 'category', 'price')
        }),
        (_('Test Details'), {
            'fields': ('unit', 'sample_type', 'processing_time_hours', 'normal_range_en', 'normal_range_ar')
        }),
        (_('Descriptions'), {
            'fields': ('description_en', 'description_ar', 'preparation_instructions_en', 'preparation_instructions_ar')
        }),
        (_('Status'), {
            'fields': ('is_active', 'created_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
