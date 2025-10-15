from django.db import models
from apps.accounts.models import User
from django.utils import timezone


class AuditLog(models.Model):
    """Audit log for tracking user actions and system events"""
    ACTION_TYPES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('system', 'System Event'),
        ('integration', 'Integration'),
    ]
    
    RESULT_TYPES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    resource_type = models.CharField(max_length=100, help_text="Type of resource being acted upon")
    resource_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID of the resource")
    description = models.TextField()
    result = models.CharField(max_length=20, choices=RESULT_TYPES, default='success')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    request_path = models.CharField(max_length=500, blank=True, null=True)
    request_method = models.CharField(max_length=10, blank=True, null=True)
    old_values = models.JSONField(default=dict, blank=True, help_text="Previous values for updates")
    new_values = models.JSONField(default=dict, blank=True, help_text="New values for updates")
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
            models.Index(fields=['resource_type', '-timestamp']),
            models.Index(fields=['result', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action_type} {self.resource_type} by {self.user.username if self.user else 'System'}"


class SystemLog(models.Model):
    """System logs for tracking application events"""
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    COMPONENT_CHOICES = [
        ('auth', 'Authentication'),
        ('dashboard', 'Dashboard'),
        ('monitoring', 'Monitoring'),
        ('analytics', 'Analytics'),
        ('notifications', 'Notifications'),
        ('audit', 'Audit'),
        ('integration', 'Integration'),
        ('database', 'Database'),
        ('api', 'API'),
        ('system', 'System'),
    ]
    
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    component = models.CharField(max_length=20, choices=COMPONENT_CHOICES)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='system_logs')
    request_id = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "System Log"
        verbose_name_plural = "System Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['level', '-timestamp']),
            models.Index(fields=['component', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.level} - {self.component}: {self.message[:50]}"


class SecurityEvent(models.Model):
    """Security-related events and incidents"""
    EVENT_TYPES = [
        ('login_attempt', 'Login Attempt'),
        ('failed_login', 'Failed Login'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('permission_denied', 'Permission Denied'),
        ('data_access', 'Data Access'),
        ('data_modification', 'Data Modification'),
        ('system_breach', 'System Breach'),
        ('malware_detected', 'Malware Detected'),
        ('unauthorized_access', 'Unauthorized Access'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    title = models.CharField(max_length=200)
    description = models.TextField()
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='security_events')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    request_path = models.CharField(max_length=500, blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_security_events')
    resolution_notes = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Security Event"
        verbose_name_plural = "Security Events"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', '-timestamp']),
            models.Index(fields=['severity', '-timestamp']),
            models.Index(fields=['is_resolved', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.severity})"


class DataAccessLog(models.Model):
    """Log of data access for compliance and security"""
    ACCESS_TYPES = [
        ('view', 'View'),
        ('export', 'Export'),
        ('print', 'Print'),
        ('download', 'Download'),
        ('api_access', 'API Access'),
    ]
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES)
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100, blank=True, null=True)
    resource_name = models.CharField(max_length=200, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    request_path = models.CharField(max_length=500, blank=True, null=True)
    data_fields = models.JSONField(default=list, blank=True, help_text="Fields that were accessed")
    purpose = models.CharField(max_length=200, blank=True, null=True, help_text="Purpose of access")
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Data Access Log"
        verbose_name_plural = "Data Access Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['access_type', '-timestamp']),
            models.Index(fields=['resource_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.access_type} {self.resource_type}"


class ComplianceReport(models.Model):
    """Compliance reports for regulatory requirements"""
    REPORT_TYPES = [
        ('hipaa', 'HIPAA'),
        ('gdpr', 'GDPR'),
        ('sox', 'SOX'),
        ('pci', 'PCI DSS'),
        ('custom', 'Custom'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    generated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    findings = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Compliance Report"
        verbose_name_plural = "Compliance Reports"
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.name} ({self.report_type})"


class AuditConfiguration(models.Model):
    """Configuration for audit logging"""
    component = models.CharField(max_length=50, unique=True)
    is_enabled = models.BooleanField(default=True)
    log_level = models.CharField(max_length=10, choices=SystemLog.LOG_LEVELS, default='INFO')
    retention_days = models.IntegerField(default=365)
    log_actions = models.JSONField(default=list, help_text="Actions to log for this component")
    exclude_users = models.JSONField(default=list, help_text="Users to exclude from logging")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Audit Configuration"
        verbose_name_plural = "Audit Configurations"
        ordering = ['component']
    
    def __str__(self):
        return f"Audit Config for {self.component}"


