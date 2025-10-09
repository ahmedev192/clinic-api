from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ModuleConnection(models.Model):
    """Module connection configurations"""
    MODULE_TYPES = [
        ('auth', 'Authentication'),
        ('patient', 'Patient Management'),
        ('doctor', 'Doctor & Staff'),
        ('appointment', 'Appointments'),
        ('consultation', 'Consultation'),
        ('billing', 'Billing'),
        ('pharmacy', 'Pharmacy'),
        ('laboratory', 'Laboratory'),
        ('inventory', 'Inventory'),
        ('reporting', 'Reporting'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('testing', 'Testing'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    module_type = models.CharField(max_length=20, choices=MODULE_TYPES)
    base_url = models.URLField()
    api_version = models.CharField(max_length=10, default='v1')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    is_enabled = models.BooleanField(default=True)
    timeout = models.IntegerField(default=30, help_text="Request timeout in seconds")
    retry_attempts = models.IntegerField(default=3)
    authentication_type = models.CharField(max_length=20, choices=[
        ('none', 'None'),
        ('api_key', 'API Key'),
        ('token', 'Token'),
        ('basic', 'Basic Auth'),
        ('oauth', 'OAuth'),
    ], default='none')
    auth_config = models.JSONField(default=dict, blank=True, help_text="Authentication configuration")
    last_checked = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Module Connection"
        verbose_name_plural = "Module Connections"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.module_type})"


class APICall(models.Model):
    """Log of API calls to external modules"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
    ]
    
    connection = models.ForeignKey(ModuleConnection, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10, choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True, help_text="Response time in seconds")
    error_message = models.TextField(blank=True, null=True)
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "API Call"
        verbose_name_plural = "API Calls"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['connection', '-timestamp']),
            models.Index(fields=['status', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.connection.name} - {self.method} {self.endpoint}"


class DataSync(models.Model):
    """Data synchronization configurations"""
    SYNC_TYPES = [
        ('one_way', 'One Way'),
        ('two_way', 'Two Way'),
        ('real_time', 'Real Time'),
        ('scheduled', 'Scheduled'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('error', 'Error'),
        ('completed', 'Completed'),
    ]
    
    name = models.CharField(max_length=200)
    source_module = models.ForeignKey(ModuleConnection, on_delete=models.CASCADE, related_name='source_syncs')
    target_module = models.ForeignKey(ModuleConnection, on_delete=models.CASCADE, related_name='target_syncs')
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    source_endpoint = models.CharField(max_length=200)
    target_endpoint = models.CharField(max_length=200)
    mapping_config = models.JSONField(default=dict, help_text="Field mapping configuration")
    schedule_config = models.JSONField(default=dict, help_text="Schedule configuration for scheduled syncs")
    is_enabled = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    next_sync = models.DateTimeField(null=True, blank=True)
    sync_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Data Sync"
        verbose_name_plural = "Data Syncs"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.source_module.name} -> {self.target_module.name})"


class SyncLog(models.Model):
    """Log of data synchronization operations"""
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    sync = models.ForeignKey(DataSync, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    records_processed = models.IntegerField(default=0)
    records_successful = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    details = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True, help_text="Duration in seconds")
    
    class Meta:
        verbose_name = "Sync Log"
        verbose_name_plural = "Sync Logs"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.sync.name} - {self.status}"


class WebhookEndpoint(models.Model):
    """Webhook endpoints for receiving data from other modules"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ]
    
    name = models.CharField(max_length=200)
    module_type = models.CharField(max_length=20, choices=ModuleConnection.MODULE_TYPES)
    endpoint_path = models.CharField(max_length=200, unique=True)
    secret_key = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_enabled = models.BooleanField(default=True)
    handler_function = models.CharField(max_length=100, help_text="Function to handle webhook data")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Webhook Endpoint"
        verbose_name_plural = "Webhook Endpoints"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.module_type})"


class WebhookLog(models.Model):
    """Log of webhook calls received"""
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('ignored', 'Ignored'),
    ]
    
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    payload = models.JSONField(default=dict)
    headers = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    response_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, null=True)
    processing_time = models.FloatField(null=True, blank=True, help_text="Processing time in seconds")
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Webhook Log"
        verbose_name_plural = "Webhook Logs"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.endpoint.name} - {self.status}"


class IntegrationTest(models.Model):
    """Integration tests for module connections"""
    TEST_TYPES = [
        ('connectivity', 'Connectivity'),
        ('authentication', 'Authentication'),
        ('data_retrieval', 'Data Retrieval'),
        ('data_submission', 'Data Submission'),
        ('full_integration', 'Full Integration'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    name = models.CharField(max_length=200)
    connection = models.ForeignKey(ModuleConnection, on_delete=models.CASCADE)
    test_type = models.CharField(max_length=20, choices=TEST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    test_config = models.JSONField(default=dict, help_text="Test configuration")
    expected_result = models.JSONField(default=dict, blank=True, help_text="Expected test result")
    actual_result = models.JSONField(default=dict, blank=True, help_text="Actual test result")
    error_message = models.TextField(blank=True, null=True)
    run_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True, help_text="Test duration in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Integration Test"
        verbose_name_plural = "Integration Tests"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.test_type})"
