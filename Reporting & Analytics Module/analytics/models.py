"""
Analytics models for the Clinic Management System.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from modeltranslation.translator import translator, TranslationOptions
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class ReportTemplate(models.Model):
    """
    Template for custom reports that can be saved and reused.
    """
    REPORT_TYPES = [
        ('financial', _('Financial Report')),
        ('demographic', _('Patient Demographics')),
        ('doctor_performance', _('Doctor Performance')),
        ('appointment_stats', _('Appointment Statistics')),
        ('custom', _('Custom Report')),
    ]
    
    AGGREGATION_TYPES = [
        ('sum', _('Sum')),
        ('avg', _('Average')),
        ('count', _('Count')),
        ('min', _('Minimum')),
        ('max', _('Maximum')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_('Template Name'))
    name_ar = models.CharField(max_length=200, verbose_name=_('Template Name (Arabic)'), blank=True)
    description = models.TextField(verbose_name=_('Description'), blank=True)
    description_ar = models.TextField(verbose_name=_('Description (Arabic)'), blank=True)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES, verbose_name=_('Report Type'))
    
    # Template configuration
    modules = models.JSONField(default=list, verbose_name=_('Included Modules'))
    filters = models.JSONField(default=dict, verbose_name=_('Default Filters'))
    date_range = models.JSONField(default=dict, verbose_name=_('Date Range Configuration'))
    aggregation_fields = models.JSONField(default=list, verbose_name=_('Aggregation Fields'))
    group_by_fields = models.JSONField(default=list, verbose_name=_('Group By Fields'))
    
    # Export settings
    export_formats = models.JSONField(default=['csv'], verbose_name=_('Available Export Formats'))
    include_charts = models.BooleanField(default=False, verbose_name=_('Include Charts'))
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    
    class Meta:
        verbose_name = _('Report Template')
        verbose_name_plural = _('Report Templates')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ReportQuery(models.Model):
    """
    Individual report queries with parameters and results.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Template'))
    name = models.CharField(max_length=200, verbose_name=_('Query Name'))
    name_ar = models.CharField(max_length=200, verbose_name=_('Query Name (Arabic)'), blank=True)
    
    # Query parameters
    report_type = models.CharField(max_length=50, verbose_name=_('Report Type'))
    filters = models.JSONField(default=dict, verbose_name=_('Query Filters'))
    date_from = models.DateTimeField(verbose_name=_('Date From'))
    date_to = models.DateTimeField(verbose_name=_('Date To'))
    group_by = models.JSONField(default=list, verbose_name=_('Group By Fields'))
    aggregation = models.JSONField(default=dict, verbose_name=_('Aggregation Settings'))
    
    # Execution details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Started At'))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Completed At'))
    
    # Error handling
    error_message = models.TextField(blank=True, verbose_name=_('Error Message'))
    retry_count = models.PositiveIntegerField(default=0, verbose_name=_('Retry Count'))
    
    class Meta:
        verbose_name = _('Report Query')
        verbose_name_plural = _('Report Queries')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"


class ReportResult(models.Model):
    """
    Results of executed report queries.
    """
    query = models.OneToOneField(ReportQuery, on_delete=models.CASCADE, verbose_name=_('Query'))
    
    # Result data
    data = models.JSONField(verbose_name=_('Report Data'))
    summary = models.JSONField(default=dict, verbose_name=_('Summary Statistics'))
    metadata = models.JSONField(default=dict, verbose_name=_('Metadata'))
    
    # Export files
    csv_file = models.FileField(upload_to='reports/csv/', null=True, blank=True, verbose_name=_('CSV File'))
    excel_file = models.FileField(upload_to='reports/excel/', null=True, blank=True, verbose_name=_('Excel File'))
    pdf_file = models.FileField(upload_to='reports/pdf/', null=True, blank=True, verbose_name=_('PDF File'))
    
    # Cache information
    cache_key = models.CharField(max_length=255, unique=True, verbose_name=_('Cache Key'))
    expires_at = models.DateTimeField(verbose_name=_('Expires At'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Report Result')
        verbose_name_plural = _('Report Results')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Result for {self.query.name}"


class DataSource(models.Model):
    """
    Configuration for external data sources.
    """
    SOURCE_TYPES = [
        ('database', _('Database')),
        ('api', _('API')),
        ('file', _('File')),
    ]
    
    name = models.CharField(max_length=100, verbose_name=_('Source Name'))
    name_ar = models.CharField(max_length=100, verbose_name=_('Source Name (Arabic)'), blank=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, verbose_name=_('Source Type'))
    connection_config = models.JSONField(verbose_name=_('Connection Configuration'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    last_sync = models.DateTimeField(null=True, blank=True, verbose_name=_('Last Sync'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Data Source')
        verbose_name_plural = _('Data Sources')
    
    def __str__(self):
        return self.name


class ReportSchedule(models.Model):
    """
    Scheduled report generation.
    """
    FREQUENCY_CHOICES = [
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('yearly', _('Yearly')),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, verbose_name=_('Template'))
    name = models.CharField(max_length=200, verbose_name=_('Schedule Name'))
    name_ar = models.CharField(max_length=200, verbose_name=_('Schedule Name (Arabic)'), blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name=_('Frequency'))
    time = models.TimeField(verbose_name=_('Execution Time'))
    recipients = models.JSONField(default=list, verbose_name=_('Email Recipients'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    last_run = models.DateTimeField(null=True, blank=True, verbose_name=_('Last Run'))
    next_run = models.DateTimeField(null=True, blank=True, verbose_name=_('Next Run'))
    
    class Meta:
        verbose_name = _('Report Schedule')
        verbose_name_plural = _('Report Schedules')
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"


# Translation configurations
class ReportTemplateTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


class ReportQueryTranslationOptions(TranslationOptions):
    fields = ('name',)


class DataSourceTranslationOptions(TranslationOptions):
    fields = ('name',)


class ReportScheduleTranslationOptions(TranslationOptions):
    fields = ('name',)


# Register translations
translator.register(ReportTemplate, ReportTemplateTranslationOptions)
translator.register(ReportQuery, ReportQueryTranslationOptions)
translator.register(DataSource, DataSourceTranslationOptions)
translator.register(ReportSchedule, ReportScheduleTranslationOptions)
