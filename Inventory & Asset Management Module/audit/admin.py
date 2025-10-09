"""
Audit admin configuration
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'object_repr', 'user', 'module', 'created']
    list_filter = ['action', 'module', 'created', 'user']
    search_fields = ['object_repr', 'user__username', 'reason']
    readonly_fields = ['created', 'modified']
    date_hierarchy = 'created'
    ordering = ['-created']
    
    fieldsets = (
        ('Action Information', {
            'fields': ('action', 'object_repr', 'module')
        }),
        ('User Information', {
            'fields': ('user', 'session_key', 'ip_address', 'user_agent')
        }),
        ('Object Information', {
            'fields': ('content_type', 'object_id')
        }),
        ('Change Details', {
            'fields': ('changes', 'old_values', 'new_values'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('reason', 'created', 'modified')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
