"""
Admin configuration for OAuth2 app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import OAuth2Provider, OAuth2Session, ExternalAccount, OAuth2Token, OAuth2AuditLog


@admin.register(OAuth2Provider)
class OAuth2ProviderAdmin(admin.ModelAdmin):
    """Admin configuration for OAuth2Provider model."""
    
    list_display = [
        'display_name', 'name', 'provider_type', 'is_active', 
        'supports_oidc', 'jit_provisioning', 'created_at'
    ]
    list_filter = [
        'provider_type', 'is_active', 'supports_oidc', 
        'jit_provisioning', 'created_at'
    ]
    search_fields = ['name', 'display_name', 'client_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['display_name']
    
    fieldsets = (
        (None, {'fields': ('id', 'name', 'display_name', 'provider_type', 'is_active')}),
        ('OAuth2 Configuration', {
            'fields': (
                'client_id', 'client_secret', 'authorization_url', 
                'token_url', 'user_info_url', 'jwks_url', 'discovery_url'
            )
        }),
        ('Scopes', {'fields': ('scopes', 'default_scopes')}),
        ('OIDC Configuration', {
            'fields': ('supports_oidc', 'issuer', 'pkce_required', 'state_required', 'nonce_required')
        }),
        ('Redirect URIs', {'fields': ('redirect_uris',)}),
        ('Claim Mapping', {
            'fields': ('claim_mapping', 'group_claim', 'role_claim')
        }),
        ('Token Configuration', {
            'fields': ('access_token_lifetime', 'refresh_token_lifetime')
        }),
        ('JIT Provisioning', {
            'fields': ('jit_provisioning', 'auto_assign_roles', 'require_email_verification')
        }),
        ('Metadata', {'fields': ('created_by', 'created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('created_by')


@admin.register(OAuth2Session)
class OAuth2SessionAdmin(admin.ModelAdmin):
    """Admin configuration for OAuth2Session model."""
    
    list_display = [
        'provider', 'user', 'external_user_id', 'is_active', 
        'created_at', 'last_used', 'is_expired'
    ]
    list_filter = [
        'provider', 'is_active', 'created_at', 'last_used'
    ]
    search_fields = [
        'user__email', 'external_user_id', 'external_username', 
        'external_email', 'state'
    ]
    readonly_fields = [
        'id', 'state', 'nonce', 'code_verifier', 'code_challenge', 
        'created_at', 'updated_at', 'last_used'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('id', 'provider', 'user', 'is_active')}),
        ('OAuth2 Flow', {
            'fields': (
                'state', 'nonce', 'code_verifier', 'code_challenge', 
                'code_challenge_method'
            )
        }),
        ('Tokens', {
            'fields': (
                'access_token', 'refresh_token', 'id_token', 
                'token_type', 'expires_at', 'scope'
            )
        }),
        ('External User Info', {
            'fields': (
                'external_user_id', 'external_username', 
                'external_email', 'external_claims'
            )
        }),
        ('Request Metadata', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'last_used')}),
    )
    
    def is_expired(self, obj):
        """Display if session is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('provider', 'user')


@admin.register(ExternalAccount)
class ExternalAccountAdmin(admin.ModelAdmin):
    """Admin configuration for ExternalAccount model."""
    
    list_display = [
        'user', 'provider', 'external_user_id', 'external_username', 
        'is_active', 'is_verified', 'created_at', 'last_used'
    ]
    list_filter = [
        'provider', 'is_active', 'is_verified', 'created_at'
    ]
    search_fields = [
        'user__email', 'external_user_id', 'external_username', 'external_email'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_used']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('id', 'user', 'provider', 'is_active', 'is_verified')}),
        ('External Account Info', {
            'fields': (
                'external_user_id', 'external_username', 
                'external_email', 'external_claims'
            )
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'last_used')}),
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user', 'provider')


@admin.register(OAuth2Token)
class OAuth2TokenAdmin(admin.ModelAdmin):
    """Admin configuration for OAuth2Token model."""
    
    list_display = [
        'user', 'provider', 'token_type', 'is_active', 
        'created_at', 'expires_at', 'is_expired'
    ]
    list_filter = [
        'provider', 'token_type', 'is_active', 'created_at', 'expires_at'
    ]
    search_fields = ['user__email', 'provider__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('id', 'user', 'provider', 'external_account', 'is_active')}),
        ('Token Data', {
            'fields': ('access_token', 'refresh_token', 'id_token')
        }),
        ('Token Metadata', {
            'fields': ('token_type', 'scope', 'expires_at')
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def is_expired(self, obj):
        """Display if token is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user', 'provider', 'external_account')


@admin.register(OAuth2AuditLog)
class OAuth2AuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for OAuth2AuditLog model."""
    
    list_display = [
        'event_type', 'provider', 'user', 'success', 
        'ip_address', 'created_at'
    ]
    list_filter = [
        'event_type', 'provider', 'success', 'created_at'
    ]
    search_fields = [
        'user__email', 'external_user_id', 'ip_address'
    ]
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('id', 'provider', 'user', 'session', 'event_type', 'success')}),
        ('Error Details', {'fields': ('error_message',)}),
        ('Request Details', {
            'fields': ('ip_address', 'user_agent', 'request_data', 'response_data')
        }),
        ('External Data', {
            'fields': ('external_user_id', 'external_claims')
        }),
        ('Timestamp', {'fields': ('created_at',)}),
    )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('provider', 'user', 'session')
    
    def has_add_permission(self, request):
        """Disable adding audit logs manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing audit logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting audit logs."""
        return False

