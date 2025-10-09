"""
Audit models for tracking system events.
"""
import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.accounts.models import User


class AuditLog(models.Model):
    """
    Comprehensive audit log for tracking all system events.
    """
    EVENT_TYPES = [
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('user_register', 'User Registration'),
        ('user_verify_email', 'Email Verification'),
        ('user_password_reset', 'Password Reset'),
        ('user_password_change', 'Password Change'),
        ('user_profile_update', 'Profile Update'),
        ('user_deactivate', 'User Deactivation'),
        ('user_activate', 'User Activation'),
        ('user_delete', 'User Deletion'),
        ('role_create', 'Role Creation'),
        ('role_update', 'Role Update'),
        ('role_delete', 'Role Deletion'),
        ('role_assign', 'Role Assignment'),
        ('role_unassign', 'Role Unassignment'),
        ('permission_create', 'Permission Creation'),
        ('permission_update', 'Permission Update'),
        ('permission_delete', 'Permission Deletion'),
        ('permission_assign', 'Permission Assignment'),
        ('permission_unassign', 'Permission Unassignment'),
        ('oauth_authorize', 'OAuth Authorization'),
        ('oauth_callback', 'OAuth Callback'),
        ('oauth_token_exchange', 'OAuth Token Exchange'),
        ('oauth_user_info', 'OAuth User Info'),
        ('oauth_jit_provisioning', 'OAuth JIT Provisioning'),
        ('oauth_account_linking', 'OAuth Account Linking'),
        ('oauth_token_refresh', 'OAuth Token Refresh'),
        ('oauth_token_revoke', 'OAuth Token Revocation'),
        ('oauth_login', 'OAuth Login'),
        ('oauth_logout', 'OAuth Logout'),
        ('admin_action', 'Admin Action'),
        ('api_access', 'API Access'),
        ('data_export', 'Data Export'),
        ('data_import', 'Data Import'),
        ('system_error', 'System Error'),
        ('security_event', 'Security Event'),
        ('other', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Event Details
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, db_index=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium')
    description = models.TextField()
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # User Information
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='audit_logs'
    )
    impersonated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='impersonated_audit_logs'
    )
    
    # Request Information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    session_key = models.CharField(max_length=40, blank=True)
    request_id = models.CharField(max_length=100, blank=True)
    
    # Object Information (Generic Foreign Key)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=255, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional Data
    metadata = models.JSONField(default=dict, blank=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    
    # External System Information
    external_system = models.CharField(max_length=100, blank=True)
    external_id = models.CharField(max_length=255, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'audit_log'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['success', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.user or 'System'} - {self.created_at}"
    
    @classmethod
    def log_event(
        cls,
        event_type,
        user=None,
        description='',
        success=True,
        error_message='',
        severity='medium',
        ip_address=None,
        user_agent='',
        session_key='',
        request_id='',
        content_object=None,
        metadata=None,
        old_values=None,
        new_values=None,
        external_system='',
        external_id='',
        impersonated_by=None
    ):
        """Create a new audit log entry."""
        return cls.objects.create(
            event_type=event_type,
            user=user,
            description=description,
            success=success,
            error_message=error_message,
            severity=severity,
            ip_address=ip_address or '127.0.0.1',
            user_agent=user_agent,
            session_key=session_key,
            request_id=request_id,
            content_object=content_object,
            metadata=metadata or {},
            old_values=old_values or {},
            new_values=new_values or {},
            external_system=external_system,
            external_id=external_id,
            impersonated_by=impersonated_by
        )


class SecurityEvent(models.Model):
    """
    Security-specific events for monitoring and alerting.
    """
    EVENT_TYPES = [
        ('failed_login', 'Failed Login Attempt'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('brute_force_attempt', 'Brute Force Attempt'),
        ('password_breach', 'Password Breach Detected'),
        ('unusual_location', 'Unusual Location Login'),
        ('unusual_time', 'Unusual Time Login'),
        ('multiple_failed_attempts', 'Multiple Failed Attempts'),
        ('admin_action', 'Admin Action'),
        ('permission_escalation', 'Permission Escalation'),
        ('data_access_violation', 'Data Access Violation'),
        ('api_abuse', 'API Abuse'),
        ('token_compromise', 'Token Compromise'),
        ('session_hijack', 'Session Hijack Attempt'),
        ('csrf_attack', 'CSRF Attack'),
        ('xss_attempt', 'XSS Attempt'),
        ('sql_injection_attempt', 'SQL Injection Attempt'),
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('invalid_token', 'Invalid Token'),
        ('expired_token', 'Expired Token'),
        ('revoked_token', 'Revoked Token'),
        ('oauth_attack', 'OAuth Attack'),
        ('other', 'Other Security Event'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
        ('ignored', 'Ignored'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Event Details
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, db_index=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    description = models.TextField()
    
    # User Information
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='security_events'
    )
    
    # Request Information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    session_key = models.CharField(max_length=40, blank=True)
    request_id = models.CharField(max_length=100, blank=True)
    
    # Additional Data
    metadata = models.JSONField(default=dict, blank=True)
    risk_score = models.PositiveIntegerField(default=0)  # 0-100
    
    # Investigation
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_security_events'
    )
    investigation_notes = models.TextField(blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'security_event'
        verbose_name = 'Security Event'
        verbose_name_plural = 'Security Events'
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['assigned_to', 'status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.user or 'Unknown'} - {self.created_at}"
    
    def resolve(self, resolution_notes='', assigned_to=None):
        """Mark the security event as resolved."""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.resolution_notes = resolution_notes
        if assigned_to:
            self.assigned_to = assigned_to
        self.save(update_fields=['status', 'resolved_at', 'resolution_notes', 'assigned_to'])


class APIAccessLog(models.Model):
    """
    API access logging for monitoring and analytics.
    """
    HTTP_METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
        ('HEAD', 'HEAD'),
        ('OPTIONS', 'OPTIONS'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Request Information
    method = models.CharField(max_length=10, choices=HTTP_METHODS)
    path = models.CharField(max_length=500)
    query_params = models.JSONField(default=dict, blank=True)
    request_headers = models.JSONField(default=dict, blank=True)
    request_body = models.TextField(blank=True)
    
    # Response Information
    status_code = models.PositiveIntegerField()
    response_headers = models.JSONField(default=dict, blank=True)
    response_body = models.TextField(blank=True)
    response_size = models.PositiveIntegerField(default=0)
    
    # User Information
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='api_access_logs'
    )
    
    # Request Metadata
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    session_key = models.CharField(max_length=40, blank=True)
    request_id = models.CharField(max_length=100, blank=True)
    
    # Performance
    processing_time = models.FloatField()  # in seconds
    database_queries = models.PositiveIntegerField(default=0)
    cache_hits = models.PositiveIntegerField(default=0)
    cache_misses = models.PositiveIntegerField(default=0)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'api_access_log'
        verbose_name = 'API Access Log'
        verbose_name_plural = 'API Access Logs'
        indexes = [
            models.Index(fields=['method', 'path', 'created_at']),
            models.Index(fields=['status_code', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['processing_time']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code} - {self.created_at}"

