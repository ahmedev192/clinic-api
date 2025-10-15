"""
Django signals for the appointments app.

Handles automatic creation of reminders and audit logging.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Appointment, Reminder, AppointmentAuditLog, ClinicSettings
from .services import ReminderService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Appointment)
def create_appointment_reminders(sender, instance, created, **kwargs):
    """
    Automatically create reminders for new appointments.
    """
    if created and instance.status in ['scheduled', 'confirmed']:
        try:
            # Get clinic settings for reminder configuration
            settings = ClinicSettings.get_settings()
            reminder_hours = settings.reminder_hours_before or [24, 2]  # Default: 24h and 2h before
            
            # Create reminders for each configured time
            for hours_before in reminder_hours:
                # Create reminder message template
                message_template = {
                    'en': f"Reminder: You have an appointment with Dr. {instance.doctor.full_name} on {instance.appointment_date} at {instance.appointment_time}. Appointment Code: {instance.appointment_code}",
                    'ar': f"تذكير: لديك موعد مع د. {instance.doctor.full_name_ar} في {instance.appointment_date} الساعة {instance.appointment_time}. رمز الموعد: {instance.appointment_code}"
                }
                
                # Create reminder (default to email, can be configured per clinic)
                ReminderService.schedule_reminder(
                    appointment_id=str(instance.id),
                    reminder_type='email',
                    hours_before=hours_before,
                    message_template=message_template
                )
                
            logger.info(f"Created reminders for appointment {instance.appointment_code}")
            
        except Exception as e:
            logger.error(f"Failed to create reminders for appointment {instance.appointment_code}: {str(e)}")


@receiver(pre_save, sender=Appointment)
def log_appointment_changes(sender, instance, **kwargs):
    """
    Log appointment changes for audit purposes.
    """
    if instance.pk:  # Only for updates, not creation
        try:
            old_instance = Appointment.objects.get(pk=instance.pk)
            
            # Check if important fields have changed
            changes = {}
            fields_to_track = [
                'status', 'appointment_date', 'appointment_time', 
                'reason_for_visit', 'notes', 'internal_notes'
            ]
            
            for field in fields_to_track:
                old_value = getattr(old_instance, field)
                new_value = getattr(instance, field)
                
                if old_value != new_value:
                    changes[field] = {
                        'old': old_value,
                        'new': new_value
                    }
            
            # Log the changes if any
            if changes:
                AppointmentAuditLog.objects.create(
                    appointment=instance,
                    action='updated',
                    performed_by=None,  # Will be set by the view if available
                    old_values={field: data['old'] for field, data in changes.items()},
                    new_values={field: data['new'] for field, data in changes.items()}
                )
                
        except Appointment.DoesNotExist:
            # This is a new appointment, not an update
            pass
        except Exception as e:
            logger.error(f"Failed to log appointment changes: {str(e)}")


@receiver(post_save, sender=Appointment)
def handle_appointment_status_changes(sender, instance, created, **kwargs):
    """
    Handle special actions when appointment status changes.
    """
    if not created:  # Only for updates
        try:
            # Get the old instance to compare status
            old_instance = Appointment.objects.get(pk=instance.pk)
            
            # If appointment was cancelled, cancel all pending reminders
            if (old_instance.status != 'cancelled' and 
                instance.status == 'cancelled'):
                
                pending_reminders = Reminder.objects.filter(
                    appointment=instance,
                    is_sent=False
                )
                
                for reminder in pending_reminders:
                    reminder.delivery_status = 'cancelled'
                    reminder.save()
                
                logger.info(f"Cancelled pending reminders for appointment {instance.appointment_code}")
            
            # If appointment was completed, mark all reminders as completed
            elif (old_instance.status != 'completed' and 
                  instance.status == 'completed'):
                
                pending_reminders = Reminder.objects.filter(
                    appointment=instance,
                    is_sent=False
                )
                
                for reminder in pending_reminders:
                    reminder.delivery_status = 'completed'
                    reminder.save()
                
                logger.info(f"Marked reminders as completed for appointment {instance.appointment_code}")
                
        except Appointment.DoesNotExist:
            # This is a new appointment, not an update
            pass
        except Exception as e:
            logger.error(f"Failed to handle appointment status changes: {str(e)}")
