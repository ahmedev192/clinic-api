"""
Admin configuration for analytics models.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    ReportTemplate, ReportQuery, ReportResult, 
    DataSource, ReportSchedule
)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_ar', 'report_type', 'created_by', 'created_at', 'is_active']
    list_filter = ['report_type', 'is_active', 'created_at']
    search_fields = ['name', 'name_ar', 'description', 'description_ar']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'name_ar', 'description', 'description_ar', 'report_type')
        }),
        (_('Configuration'), {
            'fields': ('modules', 'filters', 'date_range', 'aggregation_fields', 'group_by_fields')
        }),
        (_('Export Settings'), {
            'fields': ('export_formats', 'include_charts')
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at', 'is_active')
        })
    )


@admin.register(ReportQuery)
class ReportQueryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_ar', 'report_type', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'report_type', 'created_at']
    search_fields = ['name', 'name_ar']
    readonly_fields = ['created_at', 'started_at', 'completed_at', 'error_message', 'retry_count']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'name_ar', 'template', 'report_type')
        }),
        (_('Query Parameters'), {
            'fields': ('filters', 'date_from', 'date_to', 'group_by', 'aggregation')
        }),
        (_('Execution Status'), {
            'fields': ('status', 'created_by', 'created_at', 'started_at', 'completed_at', 'error_message', 'retry_count')
        })
    )


@admin.register(ReportResult)
class ReportResultAdmin(admin.ModelAdmin):
    list_display = ['query', 'created_at', 'expires_at']
    list_filter = ['created_at', 'expires_at']
    search_fields = ['query__name', 'query__name_ar']
    readonly_fields = ['created_at', 'cache_key']
    fieldsets = (
        (_('Query Information'), {
            'fields': ('query',)
        }),
        (_('Result Data'), {
            'fields': ('data', 'summary', 'metadata')
        }),
        (_('Export Files'), {
            'fields': ('csv_file', 'excel_file', 'pdf_file')
        }),
        (_('Cache Information'), {
            'fields': ('cache_key', 'expires_at', 'created_at')
        })
    )


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_ar', 'source_type', 'is_active', 'last_sync', 'created_at']
    list_filter = ['source_type', 'is_active', 'created_at']
    search_fields = ['name', 'name_ar']
    readonly_fields = ['created_at', 'updated_at', 'last_sync']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'name_ar', 'source_type')
        }),
        (_('Configuration'), {
            'fields': ('connection_config', 'is_active')
        }),
        (_('Sync Information'), {
            'fields': ('last_sync', 'created_at', 'updated_at')
        })
    )


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_ar', 'template', 'frequency', 'is_active', 'next_run', 'created_by']
    list_filter = ['frequency', 'is_active', 'created_at']
    search_fields = ['name', 'name_ar']
    readonly_fields = ['created_at', 'last_run', 'next_run']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'name_ar', 'template')
        }),
        (_('Schedule Configuration'), {
            'fields': ('frequency', 'time', 'recipients', 'is_active')
        }),
        (_('Execution Information'), {
            'fields': ('created_by', 'created_at', 'last_run', 'next_run')
        })
    )
