"""
Patient Management Signals

This module provides Django signals for patient management operations.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Patient, PatientSearchLog
from audit_logs.models import PatientAccessLog


@receiver(pre_save, sender=Patient)
def update_patient_timestamps(sender, instance, **kwargs):
    """Update timestamps when patient is modified"""
    if instance.pk:
        # This is an update
        instance.updated_at = timezone.now()


@receiver(post_save, sender=Patient)
def log_patient_access(sender, instance, created, **kwargs):
    """Log patient access when patient is created or updated"""
    if created:
        # Log creation access
        PatientAccessLog.objects.create(
            patient=instance,
            user=instance.created_by,
            access_type='create',
            reason='Patient record created'
        )
    else:
        # Log update access
        PatientAccessLog.objects.create(
            patient=instance,
            user=instance.updated_by,
            access_type='edit',
            reason='Patient record updated'
        )
