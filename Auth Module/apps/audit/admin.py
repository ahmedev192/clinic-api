"""
Admin configuration for audit app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, SecurityEvent, APIAccessLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for AuditLog model."""
    
    list_display = [
        'event_type', 'user', 'severity', 'success', 'ip_address', 'created_at'
    ]
    list_filter = [
        'event_type', 'severity', 'success', 'created_at', 'user'
    ]
    search_fields = [
        'user__email', 'description', 'ip_address', 'request_id'
    ]
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {'fields': ('id', 'event_type', 'severity', 'success', 'description')}),
        ('User Information', {
            'fields': ('user', 'impersonated_by')
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent', 'session_key', 'request_id')
        }),
        ('Object Information', {
            'fields': ('content_type', 'object_id', 'content_object')
        }),
        ('Additional Data', {
            'fields': ('metadata', 'old_values', 'new_values')
        }),
        ('External System', {
            'fields': ('external_system', 'external_id')
        }),
        ('Error Information', {
            'fields': ('error_message',)
        }),
        ('Timestamp', {'fields': ('created_at',)}),
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user', 'impersonated_by', 'content_type')
    
    def has_add_permission(self, request):
        """Disable adding audit logs manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing audit logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting audit logs."""
        return False


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    """Admin configuration for SecurityEvent model."""
    
    list_display = [
        'event_type', 'user', 'severity', 'status', 'risk_score', 
        'assigned_to', 'created_at', 'resolved_at'
    ]
    list_filter = [
        'event_type', 'severity', 'status', 'created_at', 'resolved_at'
    ]
    search_fields = [
        'user__email', 'description', 'ip_address', 'investigation_notes'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {'fields': ('id', 'event_type', 'severity', 'status', 'description')}),
        ('User Information', {'fields': ('user',)}),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent', 'session_key', 'request_id')
        }),
        ('Additional Data', {'fields': ('metadata', 'risk_score')}),
        ('Investigation', {
            'fields': ('assigned_to', 'investigation_notes', 'resolution_notes')
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'resolved_at')}),
    )
    
    actions = ['mark_as_investigating', 'mark_as_resolved', 'mark_as_false_positive']
    
    def mark_as_investigating(self, request, queryset):
        """Mark selected events as investigating."""
        updated = queryset.update(status='investigating', assigned_to=request.user)
        self.message_user(request, f'{updated} security events marked as investigating.')
    mark_as_investigating.short_description = 'Mark as investigating'
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected events as resolved."""
        from django.utils import timezone
        updated = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{updated} security events marked as resolved.')
    mark_as_resolved.short_description = 'Mark as resolved'
    
    def mark_as_false_positive(self, request, queryset):
        """Mark selected events as false positive."""
        updated = queryset.update(status='false_positive')
        self.message_user(request, f'{updated} security events marked as false positive.')
    mark_as_false_positive.short_description = 'Mark as false positive'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user', 'assigned_to')


@admin.register(APIAccessLog)
class APIAccessLogAdmin(admin.ModelAdmin):
    """Admin configuration for APIAccessLog model."""
    
    list_display = [
        'method', 'path', 'status_code', 'user', 'processing_time', 
        'database_queries', 'created_at'
    ]
    list_filter = [
        'method', 'status_code', 'created_at', 'user'
    ]
    search_fields = [
        'user__email', 'path', 'ip_address', 'request_id'
    ]
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {'fields': ('id', 'method', 'path', 'status_code')}),
        ('Request Information', {
            'fields': ('query_params', 'request_headers', 'request_body')
        }),
        ('Response Information', {
            'fields': ('response_headers', 'response_body', 'response_size')
        }),
        ('User Information', {'fields': ('user',)}),
        ('Request Metadata', {
            'fields': ('ip_address', 'user_agent', 'session_key', 'request_id')
        }),
        ('Performance', {
            'fields': ('processing_time', 'database_queries', 'cache_hits', 'cache_misses')
        }),
        ('Timestamp', {'fields': ('created_at',)}),
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        """Disable adding API access logs manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing API access logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting API access logs."""
        return False

