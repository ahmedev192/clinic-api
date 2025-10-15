"""
Audit admin configuration
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, SystemLog, SecurityEvent, DataAccessLog, ComplianceReport, AuditConfiguration


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'resource_type', 'user', 'result', 'timestamp']
    list_filter = ['action_type', 'result', 'timestamp', 'user']
    search_fields = ['description', 'user__username', 'resource_type']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Action Information', {
            'fields': ('action_type', 'resource_type', 'resource_id', 'description')
        }),
        ('User Information', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Request Information', {
            'fields': ('request_path', 'request_method')
        }),
        ('Change Details', {
            'fields': ('old_values', 'new_values', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Result', {
            'fields': ('result', 'timestamp')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'component', 'message_short', 'user', 'timestamp']
    list_filter = ['level', 'component', 'timestamp', 'user']
    search_fields = ['message', 'user__username']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def message_short(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_short.short_description = 'Message'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'severity', 'is_resolved', 'timestamp']
    list_filter = ['event_type', 'severity', 'is_resolved', 'timestamp']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['timestamp', 'resolved_at']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_type', 'severity', 'title', 'description')
        }),
        ('User Information', {
            'fields': ('user', 'ip_address', 'user_agent', 'request_path')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_at', 'resolved_by', 'resolution_notes')
        }),
        ('Metadata', {
            'fields': ('metadata', 'timestamp')
        }),
    )


@admin.register(DataAccessLog)
class DataAccessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'access_type', 'resource_type', 'resource_name', 'timestamp']
    list_filter = ['access_type', 'resource_type', 'timestamp', 'user']
    search_fields = ['user__username', 'resource_name', 'resource_type']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'status', 'generated_by', 'generated_at']
    list_filter = ['report_type', 'status', 'generated_at']
    search_fields = ['name', 'generated_by__username']
    readonly_fields = ['generated_at']
    date_hierarchy = 'generated_at'
    ordering = ['-generated_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('name', 'report_type', 'status')
        }),
        ('Period', {
            'fields': ('period_start', 'period_end')
        }),
        ('Generation', {
            'fields': ('generated_by', 'generated_at', 'file_path', 'file_size')
        }),
        ('Content', {
            'fields': ('summary', 'findings', 'recommendations', 'metadata')
        }),
    )


@admin.register(AuditConfiguration)
class AuditConfigurationAdmin(admin.ModelAdmin):
    list_display = ['component', 'is_enabled', 'log_level', 'retention_days', 'updated_at']
    list_filter = ['is_enabled', 'log_level', 'updated_at']
    search_fields = ['component']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Configuration', {
            'fields': ('component', 'is_enabled', 'log_level', 'retention_days')
        }),
        ('Settings', {
            'fields': ('log_actions', 'exclude_users')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )