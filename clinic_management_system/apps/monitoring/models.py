from django.db import models
from apps.accounts.models import User
from django.utils import timezone


class SystemHealth(models.Model):
    """System health monitoring"""
    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('unknown', 'Unknown'),
    ]
    
    component = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    message = models.TextField(blank=True, null=True)
    last_checked = models.DateTimeField(auto_now=True)
    response_time = models.FloatField(null=True, blank=True, help_text="Response time in seconds")
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "System Health"
        verbose_name_plural = "System Health"
        ordering = ['component']
    
    def __str__(self):
        return f"{self.component}: {self.status}"


class ModuleConnectivity(models.Model):
    """Module connectivity status"""
    STATUS_CHOICES = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
        ('timeout', 'Timeout'),
    ]
    
    module_name = models.CharField(max_length=50, unique=True)
    base_url = models.URLField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disconnected')
    last_checked = models.DateTimeField(auto_now=True)
    response_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Module Connectivity"
        verbose_name_plural = "Module Connectivity"
        ordering = ['module_name']
    
    def __str__(self):
        return f"{self.module_name}: {self.status}"


class SystemAlert(models.Model):
    """System alerts and notifications"""
    ALERT_TYPES = [
        ('error', 'Error'),
        ('warning', 'Warning'),
        ('info', 'Information'),
        ('success', 'Success'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    title = models.CharField(max_length=200)
    message = models.TextField()
    component = models.CharField(max_length=100, blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "System Alert"
        verbose_name_plural = "System Alerts"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_resolved', '-created_at']),
            models.Index(fields=['priority', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.priority})"


class PerformanceMetric(models.Model):
    """Performance metrics tracking"""
    METRIC_TYPES = [
        ('response_time', 'Response Time'),
        ('cpu_usage', 'CPU Usage'),
        ('memory_usage', 'Memory Usage'),
        ('disk_usage', 'Disk Usage'),
        ('database_connections', 'Database Connections'),
        ('api_calls', 'API Calls'),
        ('error_rate', 'Error Rate'),
    ]
    
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True, null=True)
    component = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Performance Metric"
        verbose_name_plural = "Performance Metrics"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', '-timestamp']),
            models.Index(fields=['component', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value}"


class ErrorLog(models.Model):
    """Error logging and tracking"""
    ERROR_TYPES = [
        ('database', 'Database Error'),
        ('api', 'API Error'),
        ('authentication', 'Authentication Error'),
        ('permission', 'Permission Error'),
        ('validation', 'Validation Error'),
        ('integration', 'Integration Error'),
        ('system', 'System Error'),
    ]
    
    error_type = models.CharField(max_length=30, choices=ERROR_TYPES)
    error_code = models.CharField(max_length=50, blank=True, null=True)
    message = models.TextField()
    stack_trace = models.TextField(blank=True, null=True)
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    component = models.CharField(max_length=100, blank=True, null=True)
    request_path = models.CharField(max_length=500, blank=True, null=True)
    request_method = models.CharField(max_length=10, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Error Log"
        verbose_name_plural = "Error Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['error_type', '-timestamp']),
            models.Index(fields=['is_resolved', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.error_type}: {self.message[:50]}"


class HealthCheck(models.Model):
    """Health check configurations"""
    CHECK_TYPES = [
        ('http', 'HTTP Check'),
        ('database', 'Database Check'),
        ('redis', 'Redis Check'),
        ('disk_space', 'Disk Space Check'),
        ('memory', 'Memory Check'),
        ('custom', 'Custom Check'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    check_type = models.CharField(max_length=20, choices=CHECK_TYPES)
    endpoint = models.CharField(max_length=500, blank=True, null=True)
    expected_status = models.IntegerField(default=200)
    timeout = models.IntegerField(default=30, help_text="Timeout in seconds")
    interval = models.IntegerField(default=60, help_text="Check interval in seconds")
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=20, choices=SystemHealth.STATUS_CHOICES, default='unknown')
    last_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Health Check"
        verbose_name_plural = "Health Checks"
        ordering = ['name']
    
    def __str__(self):
        return self.name


