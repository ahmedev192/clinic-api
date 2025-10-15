"""
Admin configuration for authorization app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Role, Permission, UserRole, RolePermission, 
    UserPermission, Resource, Action
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin configuration for Role model."""
    
    list_display = [
        'display_name', 'name', 'is_active', 'is_system', 
        'created_by', 'created_at', 'user_count'
    ]
    list_filter = ['is_active', 'is_system', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['display_name']
    
    fieldsets = (
        (None, {'fields': ('id', 'name', 'display_name', 'description')}),
        ('Status', {'fields': ('is_active', 'is_system')}),
        ('Metadata', {'fields': ('created_by', 'created_at', 'updated_at')}),
    )
    
    def user_count(self, obj):
        """Display number of users with this role."""
        count = obj.user_roles.filter(is_active=True).count()
        return format_html(
            '<a href="?user_roles__role__id__exact={}&user_roles__is_active__exact=True">{}</a>',
            obj.id, count
        )
    user_count.short_description = 'Users'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).prefetch_related('user_roles')


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin configuration for Permission model."""
    
    list_display = [
        'display_name', 'codename', 'resource', 'action', 
        'is_active', 'is_system', 'created_by', 'created_at'
    ]
    list_filter = ['is_active', 'is_system', 'resource', 'action', 'created_at']
    search_fields = ['name', 'display_name', 'description', 'resource', 'action']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['resource', 'action']
    
    fieldsets = (
        (None, {'fields': ('id', 'name', 'display_name', 'description')}),
        ('Permission Details', {'fields': ('resource', 'action')}),
        ('Status', {'fields': ('is_active', 'is_system')}),
        ('Metadata', {'fields': ('created_by', 'created_at', 'updated_at')}),
    )
    
    def codename(self, obj):
        """Display permission codename."""
        return obj.codename
    codename.short_description = 'Code Name'


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin configuration for UserRole model."""
    
    list_display = [
        'user', 'role', 'is_active', 'assigned_by', 
        'assigned_at', 'expires_at', 'is_expired'
    ]
    list_filter = ['is_active', 'assigned_at', 'expires_at', 'role']
    search_fields = ['user__email', 'role__name', 'role__display_name']
    readonly_fields = ['id', 'assigned_at']
    ordering = ['-assigned_at']
    
    fieldsets = (
        (None, {'fields': ('id', 'user', 'role')}),
        ('Assignment', {'fields': ('assigned_by', 'assigned_at', 'expires_at')}),
        ('Status', {'fields': ('is_active',)}),
    )
    
    def is_expired(self, obj):
        """Display if role assignment is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user', 'role', 'assigned_by')


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """Admin configuration for RolePermission model."""
    
    list_display = [
        'role', 'permission', 'assigned_by', 'assigned_at'
    ]
    list_filter = ['assigned_at', 'role', 'permission']
    search_fields = [
        'role__name', 'role__display_name', 
        'permission__name', 'permission__display_name'
    ]
    readonly_fields = ['id', 'assigned_at']
    ordering = ['-assigned_at']
    
    fieldsets = (
        (None, {'fields': ('id', 'role', 'permission')}),
        ('Assignment', {'fields': ('assigned_by', 'assigned_at')}),
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('role', 'permission', 'assigned_by')


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    """Admin configuration for UserPermission model."""
    
    list_display = [
        'user', 'permission', 'is_active', 'assigned_by', 
        'assigned_at', 'expires_at', 'is_expired'
    ]
    list_filter = ['is_active', 'assigned_at', 'expires_at', 'permission']
    search_fields = [
        'user__email', 'permission__name', 'permission__display_name'
    ]
    readonly_fields = ['id', 'assigned_at']
    ordering = ['-assigned_at']
    
    fieldsets = (
        (None, {'fields': ('id', 'user', 'permission')}),
        ('Assignment', {'fields': ('assigned_by', 'assigned_at', 'expires_at')}),
        ('Status', {'fields': ('is_active',)}),
    )
    
    def is_expired(self, obj):
        """Display if permission assignment is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user', 'permission', 'assigned_by')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """Admin configuration for Resource model."""
    
    list_display = [
        'display_name', 'name', 'resource_type', 'is_active', 'created_at'
    ]
    list_filter = ['resource_type', 'is_active', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['display_name']
    
    fieldsets = (
        (None, {'fields': ('id', 'name', 'display_name', 'description')}),
        ('Type', {'fields': ('resource_type',)}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    """Admin configuration for Action model."""
    
    list_display = [
        'display_name', 'name', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['display_name']
    
    fieldsets = (
        (None, {'fields': ('id', 'name', 'display_name', 'description')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

