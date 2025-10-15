"""
OAuth2/OIDC models for SSO functionality.
"""
import uuid
import json
from django.db import models
from django.utils import timezone
from apps.accounts.models import User


class OAuth2Provider(models.Model):
    """
    OAuth2/OIDC provider configuration.
    """
    PROVIDER_TYPES = [
        ('google', 'Google'),
        ('microsoft', 'Microsoft'),
        ('github', 'GitHub'),
        ('okta', 'Okta'),
        ('auth0', 'Auth0'),
        ('keycloak', 'Keycloak'),
        ('generic', 'Generic OAuth2/OIDC'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    display_name = models.CharField(max_length=150)
    provider_type = models.CharField(max_length=20, choices=PROVIDER_TYPES)
    is_active = models.BooleanField(default=True)
    
    # OAuth2 Configuration
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    authorization_url = models.URLField()
    token_url = models.URLField()
    user_info_url = models.URLField(blank=True)
    jwks_url = models.URLField(blank=True)
    discovery_url = models.URLField(blank=True)  # OIDC Discovery URL
    
    # OAuth2 Scopes
    scopes = models.JSONField(default=list, blank=True)
    default_scopes = models.JSONField(default=list, blank=True)
    
    # OIDC Configuration
    supports_oidc = models.BooleanField(default=False)
    issuer = models.URLField(blank=True)
    
    # Security Configuration
    pkce_required = models.BooleanField(default=True)
    state_required = models.BooleanField(default=True)
    nonce_required = models.BooleanField(default=False)
    
    # Redirect URIs
    redirect_uris = models.JSONField(default=list, blank=True)
    
    # Claim Mapping
    claim_mapping = models.JSONField(default=dict, blank=True)
    group_claim = models.CharField(max_length=100, blank=True)
    role_claim = models.CharField(max_length=100, blank=True)
    
    # Token Configuration
    access_token_lifetime = models.PositiveIntegerField(default=3600)  # seconds
    refresh_token_lifetime = models.PositiveIntegerField(default=1209600)  # seconds
    
    # JIT Provisioning
    jit_provisioning = models.BooleanField(default=True)
    auto_assign_roles = models.JSONField(default=list, blank=True)
    require_email_verification = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_oauth_providers'
    )
    
    class Meta:
        db_table = 'oauth2_provider'
        verbose_name = 'OAuth2 Provider'
        verbose_name_plural = 'OAuth2 Providers'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['provider_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.display_name
    
    def get_authorization_url(self, state=None, nonce=None, code_challenge=None, code_challenge_method=None):
        """Generate authorization URL with parameters."""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uris[0] if self.redirect_uris else '',
            'scope': ' '.join(self.scopes),
        }
        
        if state and self.state_required:
            params['state'] = state
        
        if nonce and self.nonce_required:
            params['nonce'] = nonce
        
        if code_challenge and self.pkce_required:
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = code_challenge_method or 'S256'
        
        # Build URL with parameters
        from urllib.parse import urlencode
        return f"{self.authorization_url}?{urlencode(params)}"
    
    def get_token_data(self, code, redirect_uri, code_verifier=None):
        """Get token exchange data."""
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
        }
        
        if code_verifier and self.pkce_required:
            data['code_verifier'] = code_verifier
        
        return data


class OAuth2Session(models.Model):
    """
    OAuth2 session tracking for SSO flows.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(OAuth2Provider, on_delete=models.CASCADE, related_name='sessions')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='oauth_sessions', null=True, blank=True)
    
    # OAuth2 Flow State
    state = models.CharField(max_length=255, unique=True, db_index=True)
    nonce = models.CharField(max_length=255, blank=True)
    code_verifier = models.CharField(max_length=255, blank=True)
    code_challenge = models.CharField(max_length=255, blank=True)
    code_challenge_method = models.CharField(max_length=10, default='S256')
    
    # Tokens
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    id_token = models.TextField(blank=True)
    
    # Token Metadata
    token_type = models.CharField(max_length=50, default='Bearer')
    expires_at = models.DateTimeField(null=True, blank=True)
    scope = models.TextField(blank=True)
    
    # External User Info
    external_user_id = models.CharField(max_length=255, blank=True)
    external_username = models.CharField(max_length=255, blank=True)
    external_email = models.EmailField(blank=True)
    external_claims = models.JSONField(default=dict, blank=True)
    
    # Session State
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used = models.DateTimeField(auto_now=True)
    
    # Request Metadata
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    class Meta:
        db_table = 'oauth2_session'
        verbose_name = 'OAuth2 Session'
        verbose_name_plural = 'OAuth2 Sessions'
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['provider', 'is_active']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['external_user_id', 'provider']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"OAuth2 Session for {self.provider.display_name}"
    
    def is_expired(self):
        """Check if the session is expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def is_valid(self):
        """Check if the session is valid (active and not expired)."""
        return self.is_active and not self.is_expired()
    
    def deactivate(self):
        """Deactivate the session."""
        self.is_active = False
        self.save(update_fields=['is_active'])


class ExternalAccount(models.Model):
    """
    External account linking for users.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='external_accounts')
    provider = models.ForeignKey(OAuth2Provider, on_delete=models.CASCADE, related_name='external_accounts')
    
    # External Account Info
    external_user_id = models.CharField(max_length=255, db_index=True)
    external_username = models.CharField(max_length=255, blank=True)
    external_email = models.EmailField(blank=True)
    external_claims = models.JSONField(default=dict, blank=True)
    
    # Account Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'external_account'
        verbose_name = 'External Account'
        verbose_name_plural = 'External Accounts'
        unique_together = ['user', 'provider', 'external_user_id']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['provider', 'external_user_id']),
            models.Index(fields=['external_user_id', 'provider']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.provider.display_name}"


class OAuth2Token(models.Model):
    """
    OAuth2 token storage for external API access.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='oauth_tokens')
    provider = models.ForeignKey(OAuth2Provider, on_delete=models.CASCADE, related_name='tokens')
    external_account = models.ForeignKey(
        ExternalAccount, 
        on_delete=models.CASCADE, 
        related_name='tokens',
        null=True,
        blank=True
    )
    
    # Token Data
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    id_token = models.TextField(blank=True)
    
    # Token Metadata
    token_type = models.CharField(max_length=50, default='Bearer')
    scope = models.TextField(blank=True)
    expires_at = models.DateTimeField()
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'oauth2_token'
        verbose_name = 'OAuth2 Token'
        verbose_name_plural = 'OAuth2 Tokens'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['provider', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"OAuth2 Token for {self.user.email} - {self.provider.display_name}"
    
    def is_expired(self):
        """Check if the token is expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if the token is valid (active and not expired)."""
        return self.is_active and not self.is_expired()
    
    def refresh_access_token(self, new_access_token, new_expires_at, new_refresh_token=None):
        """Update token with new access token."""
        self.access_token = new_access_token
        self.expires_at = new_expires_at
        if new_refresh_token:
            self.refresh_token = new_refresh_token
        self.updated_at = timezone.now()
        self.save(update_fields=['access_token', 'refresh_token', 'expires_at', 'updated_at'])
    
    def revoke(self):
        """Revoke the token."""
        self.is_active = False
        self.save(update_fields=['is_active'])


class OAuth2AuditLog(models.Model):
    """
    Audit log for OAuth2/OIDC events.
    """
    EVENT_TYPES = [
        ('authorize', 'Authorization Request'),
        ('callback', 'Callback Received'),
        ('token_exchange', 'Token Exchange'),
        ('user_info', 'User Info Retrieved'),
        ('jit_provisioning', 'JIT User Provisioning'),
        ('account_linking', 'Account Linking'),
        ('token_refresh', 'Token Refresh'),
        ('token_revoke', 'Token Revocation'),
        ('login', 'SSO Login'),
        ('logout', 'SSO Logout'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(OAuth2Provider, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='oauth_audit_logs')
    session = models.ForeignKey(OAuth2Session, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    
    # Event Details
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Request Details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    
    # External Data
    external_user_id = models.CharField(max_length=255, blank=True)
    external_claims = models.JSONField(default=dict, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'oauth2_audit_log'
        verbose_name = 'OAuth2 Audit Log'
        verbose_name_plural = 'OAuth2 Audit Logs'
        indexes = [
            models.Index(fields=['provider', 'event_type']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['success']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.provider.display_name} - {self.created_at}"



