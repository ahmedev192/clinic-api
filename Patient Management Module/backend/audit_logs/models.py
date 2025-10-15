"""
Audit Logging Models

This module provides comprehensive audit logging for all patient management operations.
Tracks all changes, access, and actions for compliance and security purposes.
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json


class AuditLog(models.Model):
    """
    Comprehensive audit log for tracking all changes and actions.
    """
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('soft_delete', 'Soft Delete'),
        ('restore', 'Restore'),
        ('view', 'View'),
        ('search', 'Search'),
        ('export', 'Export'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('permission_denied', 'Permission Denied'),
    ]
    
    # Basic Information
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='audit_logs')
    
    # Object Information (Generic Foreign Key)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Change Details
    field_name = models.CharField(max_length=100, blank=True, help_text='Field that was changed')
    old_value = models.TextField(blank=True, help_text='Previous value')
    new_value = models.TextField(blank=True, help_text='New value')
    
    # Additional Context
    description = models.TextField(help_text='Human-readable description of the action')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Request Information
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    
    # Additional Data (JSON)
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, action, content_object=None, field_name='', 
                   old_value='', new_value='', description='', 
                   ip_address=None, user_agent='', request_path='', 
                   request_method='', additional_data=None):
        """
        Convenience method to create audit log entries.
        """
        return cls.objects.create(
            user=user,
            action=action,
            content_type=ContentType.objects.get_for_model(content_object) if content_object else None,
            object_id=content_object.pk if content_object else None,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else '',
            new_value=str(new_value) if new_value is not None else '',
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            request_method=request_method,
            additional_data=additional_data or {}
        )


class PatientAccessLog(models.Model):
    """
    Specific audit log for patient data access.
    Tracks who accessed which patient records and when.
    """
    
    ACCESS_TYPE_CHOICES = [
        ('view', 'View'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('print', 'Print'),
        ('search', 'Search'),
    ]
    
    patient = models.ForeignKey('patient_management.Patient', on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='patient_access_logs')
    access_type = models.CharField(max_length=10, choices=ACCESS_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Access Details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    
    # Additional Context
    reason = models.TextField(blank=True, help_text='Reason for access if required')
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['patient', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['access_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.access_type} - {self.patient.patient_code}"


class DataExportLog(models.Model):
    """
    Log for data export operations to track data access and compliance.
    """
    
    EXPORT_TYPE_CHOICES = [
        ('patient_list', 'Patient List'),
        ('patient_details', 'Patient Details'),
        ('medical_history', 'Medical History'),
        ('allergies', 'Allergies'),
        ('documents', 'Documents'),
        ('full_export', 'Full Patient Export'),
    ]
    
    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='export_logs')
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPE_CHOICES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Export Details
    record_count = models.PositiveIntegerField(help_text='Number of records exported')
    file_size = models.PositiveIntegerField(help_text='File size in bytes')
    file_path = models.CharField(max_length=500, blank=True, help_text='Path to exported file')
    
    # Filters Applied
    filters_applied = models.JSONField(default=dict, blank=True, help_text='Filters used for export')
    
    # Access Information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['export_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.export_type} - {self.timestamp}"


class SystemEventLog(models.Model):
    """
    Log for system-level events and errors.
    """
    
    EVENT_TYPE_CHOICES = [
        ('error', 'Error'),
        ('warning', 'Warning'),
        ('info', 'Information'),
        ('security', 'Security Event'),
        ('performance', 'Performance Issue'),
    ]
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='system_event_logs')
    
    # Event Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    module = models.CharField(max_length=50, help_text='Module where event occurred')
    
    # Technical Details
    error_code = models.CharField(max_length=50, blank=True)
    stack_trace = models.TextField(blank=True)
    request_data = models.JSONField(default=dict, blank=True)
    
    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_events')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['module', 'timestamp']),
            models.Index(fields=['is_resolved', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_type.upper()} - {self.title} - {self.timestamp}"
    
    def resolve(self, user, notes=''):
        """Mark the event as resolved"""
        self.is_resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()
