from django.db import models
from apps.accounts.models import User
from django.utils import timezone


class DashboardConfiguration(models.Model):
    """Configuration settings for dashboard display"""
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('accountant', 'Accountant'),
        ('doctor', 'Doctor'),
        ('receptionist', 'Receptionist'),
        ('nurse', 'Nurse'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    enabled_widgets = models.JSONField(default=list, help_text="List of widget IDs enabled for this role")
    refresh_interval = models.IntegerField(default=30, help_text="Refresh interval in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dashboard Configuration"
        verbose_name_plural = "Dashboard Configurations"
    
    def __str__(self):
        return f"Dashboard Config for {self.get_role_display()}"


class SystemMetrics(models.Model):
    """Store system metrics for dashboard display"""
    METRIC_TYPES = [
        ('patients_total', 'Total Patients'),
        ('patients_active', 'Active Patients'),
        ('appointments_today', 'Today\'s Appointments'),
        ('appointments_pending', 'Pending Appointments'),
        ('consultations_today', 'Today\'s Consultations'),
        ('doctors_active', 'Active Doctors'),
        ('staff_total', 'Total Staff'),
        ('revenue_total', 'Total Revenue'),
        ('revenue_monthly', 'Monthly Revenue'),
        ('invoices_pending', 'Pending Invoices'),
        ('inventory_alerts', 'Inventory Alerts'),
        ('pharmacy_alerts', 'Pharmacy Alerts'),
    ]
    
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "System Metric"
        verbose_name_plural = "System Metrics"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value}"


class QuickAction(models.Model):
    """Quick actions available for different roles"""
    ACTION_TYPES = [
        ('create_patient', 'Create Patient'),
        ('schedule_appointment', 'Schedule Appointment'),
        ('view_reports', 'View Reports'),
        ('manage_inventory', 'Manage Inventory'),
        ('process_payment', 'Process Payment'),
        ('view_analytics', 'View Analytics'),
    ]
    
    name = models.CharField(max_length=100)
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    url = models.URLField()
    icon = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    roles = models.JSONField(default=list, help_text="List of roles that can access this action")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Quick Action"
        verbose_name_plural = "Quick Actions"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class DashboardWidget(models.Model):
    """Widgets that can be displayed on dashboard"""
    WIDGET_TYPES = [
        ('stat_card', 'Statistics Card'),
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('alert', 'Alert'),
        ('list', 'List'),
    ]
    
    name = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    data_source = models.CharField(max_length=100, help_text="API endpoint or data source")
    configuration = models.JSONField(default=dict, help_text="Widget-specific configuration")
    roles = models.JSONField(default=list, help_text="List of roles that can see this widget")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    size = models.CharField(max_length=20, default='medium', choices=[
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('full', 'Full Width'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dashboard Widget"
        verbose_name_plural = "Dashboard Widgets"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
