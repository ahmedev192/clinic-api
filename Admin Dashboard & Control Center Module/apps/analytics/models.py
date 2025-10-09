from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ReportTemplate(models.Model):
    """Report templates for different types of analytics"""
    REPORT_TYPES = [
        ('financial', 'Financial Report'),
        ('patient', 'Patient Report'),
        ('appointment', 'Appointment Report'),
        ('staff', 'Staff Report'),
        ('inventory', 'Inventory Report'),
        ('custom', 'Custom Report'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True, null=True)
    query_config = models.JSONField(help_text="Configuration for data queries")
    chart_config = models.JSONField(default=dict, help_text="Chart configuration")
    filters = models.JSONField(default=dict, help_text="Available filters")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Report Template"
        verbose_name_plural = "Report Templates"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class GeneratedReport(models.Model):
    """Generated reports"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    parameters = models.JSONField(default=dict, help_text="Report parameters")
    data = models.JSONField(default=dict, help_text="Report data")
    file_path = models.CharField(max_length=500, blank=True, null=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Generated Report"
        verbose_name_plural = "Generated Reports"
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.name} ({self.status})"


class AnalyticsMetric(models.Model):
    """Analytics metrics for tracking KPIs"""
    METRIC_TYPES = [
        ('revenue', 'Revenue'),
        ('patients', 'Patients'),
        ('appointments', 'Appointments'),
        ('consultations', 'Consultations'),
        ('staff_performance', 'Staff Performance'),
        ('inventory', 'Inventory'),
        ('efficiency', 'Efficiency'),
    ]
    
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    name = models.CharField(max_length=200)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=20, blank=True, null=True)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Analytics Metric"
        verbose_name_plural = "Analytics Metrics"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['metric_type', '-created_at']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.name}: {self.value}"


class DashboardWidget(models.Model):
    """Dashboard widgets for analytics display"""
    WIDGET_TYPES = [
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('kpi', 'KPI Card'),
        ('gauge', 'Gauge'),
        ('trend', 'Trend Line'),
    ]
    
    name = models.CharField(max_length=200)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    data_source = models.CharField(max_length=100, help_text="Data source configuration")
    configuration = models.JSONField(default=dict, help_text="Widget configuration")
    position = models.JSONField(default=dict, help_text="Widget position and size")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dashboard Widget"
        verbose_name_plural = "Dashboard Widgets"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DataExport(models.Model):
    """Data export records"""
    EXPORT_TYPES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(max_length=200)
    export_type = models.CharField(max_length=10, choices=EXPORT_TYPES)
    data_source = models.CharField(max_length=100)
    filters = models.JSONField(default=dict, help_text="Export filters")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Data Export"
        verbose_name_plural = "Data Exports"
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.name} ({self.export_type})"


class ScheduledReport(models.Model):
    """Scheduled reports"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=200)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    parameters = models.JSONField(default=dict, help_text="Report parameters")
    recipients = models.JSONField(default=list, help_text="Email recipients")
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Scheduled Report"
        verbose_name_plural = "Scheduled Reports"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.frequency})"
