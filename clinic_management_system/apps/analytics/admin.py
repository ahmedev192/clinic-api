"""
Admin configuration for analytics models.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    ReportTemplate, GeneratedReport, AnalyticsMetric, 
    DashboardWidget, DataExport, ScheduledReport
)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'created_by', 'created_at', 'is_active']
    list_filter = ['report_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'report_type')
        }),
        (_('Configuration'), {
            'fields': ('query_config', 'chart_config', 'filters')
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at', 'is_active')
        })
    )


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'status', 'generated_by', 'generated_at']
    list_filter = ['status', 'generated_at']
    search_fields = ['name', 'template__name']
    readonly_fields = ['generated_at', 'completed_at', 'error_message']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'template', 'status')
        }),
        (_('Parameters'), {
            'fields': ('parameters',)
        }),
        (_('Execution Status'), {
            'fields': ('generated_by', 'generated_at', 'completed_at', 'error_message', 'file_path')
        })
    )


@admin.register(AnalyticsMetric)
class AnalyticsMetricAdmin(admin.ModelAdmin):
    list_display = ['name', 'metric_type', 'value', 'unit', 'created_at']
    list_filter = ['metric_type', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    fieldsets = (
        (_('Metric Information'), {
            'fields': ('name', 'metric_type', 'value', 'unit')
        }),
        (_('Period'), {
            'fields': ('period_start', 'period_end')
        }),
        (_('Metadata'), {
            'fields': ('metadata', 'created_at')
        })
    )


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'widget_type', 'title', 'is_active', 'created_at']
    list_filter = ['widget_type', 'is_active', 'created_at']
    search_fields = ['name', 'title']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'widget_type', 'title', 'description')
        }),
        (_('Configuration'), {
            'fields': ('data_source', 'configuration', 'position')
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at', 'is_active')
        })
    )


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = ['name', 'export_type', 'status', 'requested_by', 'requested_at']
    list_filter = ['export_type', 'status', 'requested_at']
    search_fields = ['name']
    readonly_fields = ['requested_at', 'completed_at', 'error_message']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'export_type', 'data_source')
        }),
        (_('Configuration'), {
            'fields': ('filters',)
        }),
        (_('Status'), {
            'fields': ('status', 'file_path', 'file_size', 'requested_by', 'requested_at', 'completed_at', 'error_message')
        })
    )


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'frequency', 'is_active', 'next_run', 'created_by']
    list_filter = ['frequency', 'is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'last_run', 'next_run']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'template', 'frequency', 'parameters', 'recipients', 'is_active')
        }),
        (_('Execution Information'), {
            'fields': ('created_by', 'created_at', 'last_run', 'next_run')
        })
    )