from django.db import models
from apps.accounts.models import User
from django.utils import timezone


class NotificationTemplate(models.Model):
    """Notification templates for different types of alerts"""
    NOTIFICATION_TYPES = [
        ('appointment', 'Appointment'),
        ('inventory', 'Inventory'),
        ('billing', 'Billing'),
        ('system', 'System'),
        ('patient', 'Patient'),
        ('staff', 'Staff'),
        ('emergency', 'Emergency'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    name = models.CharField(max_length=200)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    title_template = models.CharField(max_length=500)
    message_template = models.TextField()
    variables = models.JSONField(default=list, help_text="Available template variables")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Notification Template"
        verbose_name_plural = "Notification Templates"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Notification(models.Model):
    """System notifications"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    CHANNEL_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('webhook', 'Webhook'),
    ]
    
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=500)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NotificationTemplate.NOTIFICATION_TYPES)
    priority = models.CharField(max_length=20, choices=NotificationTemplate.PRIORITY_CHOICES, default='medium')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='dashboard')
    recipient = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    data = models.JSONField(default=dict, help_text="Additional notification data")
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['notification_type', '-created_at']),
            models.Index(fields=['priority', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"


class NotificationRule(models.Model):
    """Rules for automatic notification generation"""
    RULE_TYPES = [
        ('threshold', 'Threshold'),
        ('schedule', 'Schedule'),
        ('event', 'Event'),
        ('condition', 'Condition'),
    ]
    
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    notification_type = models.CharField(max_length=20, choices=NotificationTemplate.NOTIFICATION_TYPES)
    conditions = models.JSONField(help_text="Rule conditions")
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Notification Rule"
        verbose_name_plural = "Notification Rules"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class NotificationSubscription(models.Model):
    """User notification subscriptions"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NotificationTemplate.NOTIFICATION_TYPES)
    channel = models.CharField(max_length=20, choices=Notification.CHANNEL_CHOICES)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Notification Subscription"
        verbose_name_plural = "Notification Subscriptions"
        unique_together = ['user', 'notification_type', 'channel']
        ordering = ['user', 'notification_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type} ({self.channel})"


class NotificationLog(models.Model):
    """Log of notification delivery attempts"""
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    channel = models.CharField(max_length=20, choices=Notification.CHANNEL_CHOICES)
    status = models.CharField(max_length=20, choices=Notification.STATUS_CHOICES)
    error_message = models.TextField(blank=True, null=True)
    response_data = models.JSONField(default=dict, blank=True)
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notification Log"
        verbose_name_plural = "Notification Logs"
        ordering = ['-attempted_at']
    
    def __str__(self):
        return f"{self.notification.title} - {self.channel} ({self.status})"


class AlertThreshold(models.Model):
    """Alert thresholds for different metrics"""
    METRIC_TYPES = [
        ('inventory_stock', 'Inventory Stock'),
        ('appointment_capacity', 'Appointment Capacity'),
        ('revenue_target', 'Revenue Target'),
        ('error_rate', 'Error Rate'),
        ('response_time', 'Response Time'),
        ('patient_wait_time', 'Patient Wait Time'),
    ]
    
    name = models.CharField(max_length=200)
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    threshold_value = models.DecimalField(max_digits=15, decimal_places=2)
    comparison_operator = models.CharField(max_length=10, choices=[
        ('gt', 'Greater Than'),
        ('gte', 'Greater Than or Equal'),
        ('lt', 'Less Than'),
        ('lte', 'Less Than or Equal'),
        ('eq', 'Equal'),
        ('ne', 'Not Equal'),
    ])
    notification_template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Alert Threshold"
        verbose_name_plural = "Alert Thresholds"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.metric_type})"


class NotificationQueue(models.Model):
    """Queue for pending notifications"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_at = models.DateTimeField(default=timezone.now)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notification Queue"
        verbose_name_plural = "Notification Queue"
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.notification.title} - {self.status}"


