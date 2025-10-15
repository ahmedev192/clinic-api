"""
Audit Logging Signals

This module provides Django signals to automatically log model changes.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import AuditLog, PatientAccessLog
from patient_management.models import Patient, MedicalHistory, Allergy, ChronicCondition, PatientDocument


@receiver(post_save, sender=Patient)
def log_patient_changes(sender, instance, created, **kwargs):
    """Log changes to Patient model"""
    if created:
        AuditLog.log_action(
            user=instance.created_by,
            action='create',
            content_object=instance,
            description=f"Created new patient: {instance.patient_code}"
        )
    else:
        # This is an update - we'll need to track what changed
        AuditLog.log_action(
            user=instance.updated_by,
            action='update',
            content_object=instance,
            description=f"Updated patient: {instance.patient_code}"
        )


@receiver(post_save, sender=MedicalHistory)
def log_medical_history_changes(sender, instance, created, **kwargs):
    """Log changes to MedicalHistory model"""
    if created:
        AuditLog.log_action(
            user=instance.created_by,
            action='create',
            content_object=instance,
            description=f"Added medical history entry for patient: {instance.patient.patient_code}"
        )
    else:
        AuditLog.log_action(
            user=instance.updated_by,
            action='update',
            content_object=instance,
            description=f"Updated medical history for patient: {instance.patient.patient_code}"
        )


@receiver(post_save, sender=Allergy)
def log_allergy_changes(sender, instance, created, **kwargs):
    """Log changes to Allergy model"""
    if created:
        AuditLog.log_action(
            user=instance.created_by,
            action='create',
            content_object=instance,
            description=f"Added allergy for patient: {instance.patient.patient_code}"
        )
    else:
        AuditLog.log_action(
            user=instance.updated_by,
            action='update',
            content_object=instance,
            description=f"Updated allergy for patient: {instance.patient.patient_code}"
        )


@receiver(post_save, sender=ChronicCondition)
def log_chronic_condition_changes(sender, instance, created, **kwargs):
    """Log changes to ChronicCondition model"""
    if created:
        AuditLog.log_action(
            user=instance.created_by,
            action='create',
            content_object=instance,
            description=f"Added chronic condition for patient: {instance.patient.patient_code}"
        )
    else:
        AuditLog.log_action(
            user=instance.updated_by,
            action='update',
            content_object=instance,
            description=f"Updated chronic condition for patient: {instance.patient.patient_code}"
        )


@receiver(post_save, sender=PatientDocument)
def log_document_changes(sender, instance, created, **kwargs):
    """Log changes to PatientDocument model"""
    if created:
        AuditLog.log_action(
            user=instance.uploaded_by,
            action='create',
            content_object=instance,
            description=f"Uploaded document for patient: {instance.patient.patient_code}"
        )
    else:
        AuditLog.log_action(
            user=instance.uploaded_by,
            action='update',
            content_object=instance,
            description=f"Updated document for patient: {instance.patient.patient_code}"
        )


@receiver(post_delete, sender=Patient)
def log_patient_deletion(sender, instance, **kwargs):
    """Log patient deletion"""
    # Note: This will only fire for hard deletes, not soft deletes
    AuditLog.log_action(
        user=instance.updated_by,
        action='delete',
        content_object=instance,
        description=f"Hard deleted patient: {instance.patient_code}"
    )


@receiver(post_delete, sender=MedicalHistory)
def log_medical_history_deletion(sender, instance, **kwargs):
    """Log medical history deletion"""
    AuditLog.log_action(
        user=instance.updated_by,
        action='delete',
        content_object=instance,
        description=f"Deleted medical history for patient: {instance.patient.patient_code}"
    )


@receiver(post_delete, sender=Allergy)
def log_allergy_deletion(sender, instance, **kwargs):
    """Log allergy deletion"""
    AuditLog.log_action(
        user=instance.updated_by,
        action='delete',
        content_object=instance,
        description=f"Deleted allergy for patient: {instance.patient.patient_code}"
    )


@receiver(post_delete, sender=ChronicCondition)
def log_chronic_condition_deletion(sender, instance, **kwargs):
    """Log chronic condition deletion"""
    AuditLog.log_action(
        user=instance.updated_by,
        action='delete',
        content_object=instance,
        description=f"Deleted chronic condition for patient: {instance.patient.patient_code}"
    )


@receiver(post_delete, sender=PatientDocument)
def log_document_deletion(sender, instance, **kwargs):
    """Log document deletion"""
    AuditLog.log_action(
        user=instance.uploaded_by,
        action='delete',
        content_object=instance,
        description=f"Deleted document for patient: {instance.patient.patient_code}"
    )
