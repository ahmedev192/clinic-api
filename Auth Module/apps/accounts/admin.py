"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, EmailVerificationToken, PasswordResetToken, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    
    list_display = [
        'email', 'full_name', 'is_verified', 'is_active', 'is_staff', 
        'provider', 'last_login', 'date_joined'
    ]
    list_filter = [
        'is_verified', 'is_active', 'is_staff', 'is_superuser', 
        'provider', 'mfa_enabled', 'date_joined'
    ]
    search_fields = ['email', 'first_name', 'last_name', 'external_id']
    ordering = ['-date_joined']
    readonly_fields = ['id', 'date_joined', 'last_login', 'last_password_change']
    
    fieldsets = (
        (None, {'fields': ('id', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'avatar')}),
        ('Permissions', {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Security', {
            'fields': ('mfa_enabled', 'failed_login_attempts', 'locked_until', 'last_password_change'),
        }),
        ('SSO', {
            'fields': ('external_id', 'provider', 'provider_data'),
        }),
        ('Preferences', {
            'fields': ('timezone', 'language'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    def full_name(self, obj):
        """Display full name."""
        return obj.full_name
    full_name.short_description = 'Full Name'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""
    
    list_display = ['user', 'company', 'job_title', 'location', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['user__email', 'company', 'job_title', 'location']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Professional', {'fields': ('company', 'job_title', 'website')}),
        ('Personal', {'fields': ('bio', 'location', 'birth_date', 'gender')}),
        ('Preferences', {'fields': ('preferences',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Admin configuration for EmailVerificationToken model."""
    
    list_display = ['user', 'token', 'is_used', 'created_at', 'expires_at', 'is_expired']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at']
    ordering = ['-created_at']
    
    def is_expired(self, obj):
        """Display if token is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin configuration for PasswordResetToken model."""
    
    list_display = ['user', 'token', 'is_used', 'created_at', 'expires_at', 'is_expired']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at']
    ordering = ['-created_at']
    
    def is_expired(self, obj):
        """Display if token is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin configuration for UserSession model."""
    
    list_display = [
        'user', 'ip_address', 'is_active', 'created_at', 
        'last_activity', 'expires_at', 'is_expired'
    ]
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['user__email', 'ip_address', 'session_key']
    readonly_fields = ['session_key', 'refresh_token', 'created_at', 'last_activity']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'session_key', 'refresh_token')}),
        ('Device Info', {'fields': ('ip_address', 'user_agent', 'device_info')}),
        ('Status', {'fields': ('is_active', 'expires_at')}),
        ('Timestamps', {'fields': ('created_at', 'last_activity')}),
    )
    
    def is_expired(self, obj):
        """Display if session is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user')

