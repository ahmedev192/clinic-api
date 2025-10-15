"""
Signals for Staff Management
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from apps.accounts.models import User
from .models import Staff, StaffAuditLog, Doctor


@receiver(post_save, sender=Staff)
def create_staff_audit_log(sender, instance, created, **kwargs):
    """Create audit log entry when staff is created or updated"""
    if created:
        action = 'created'
        field_name = ''
        old_value = ''
        new_value = f"Staff created: {instance.full_name_en}"
    else:
        action = 'updated'
        field_name = 'general'
        old_value = 'Previous values'
        new_value = 'Updated values'
    
    StaffAuditLog.objects.create(
        staff=instance,
        action=action,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        changed_by=instance.created_by
    )


@receiver(post_save, sender=Staff)
def create_doctor_profile(sender, instance, created, **kwargs):
    """Create doctor profile if staff role is doctor"""
    if created and instance.role.code in ['DOC', 'DOCTOR']:
        Doctor.objects.get_or_create(
            staff=instance,
            defaults={
                'years_of_experience': 0,
                'is_available': True,
                'is_accepting_new_patients': True
            }
        )


@receiver(pre_save, sender=Staff)
def generate_staff_id(sender, instance, **kwargs):
    """Generate staff ID if not provided"""
    if not instance.staff_id:
        instance.staff_id = instance.generate_staff_id()


@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    """Create staff profile when user is created (if needed)"""
    # This can be used for automatic staff profile creation
    # when a user is created through the admin or API
    pass

