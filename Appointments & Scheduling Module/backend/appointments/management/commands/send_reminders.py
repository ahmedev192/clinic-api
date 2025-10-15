"""
Django management command to send appointment reminders.

This command processes pending reminders and sends them via configured channels.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from appointments.services import ReminderService
from appointments.models import Reminder
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to send appointment reminders."""
    
    help = 'Send pending appointment reminders'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of reminders to process',
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        dry_run = options['dry_run']
        limit = options['limit']
        
        self.stdout.write(
            self.style.SUCCESS(f'Processing reminders (limit: {limit}, dry-run: {dry_run})')
        )
        
        try:
            # Get pending reminders
            reminders = ReminderService.get_pending_reminders()[:limit]
            
            if not reminders:
                self.stdout.write(self.style.SUCCESS('No pending reminders found.'))
                return
            
            self.stdout.write(f'Found {len(reminders)} pending reminders.')
            
            sent_count = 0
            failed_count = 0
            
            for reminder in reminders:
                try:
                    if dry_run:
                        self.stdout.write(
                            f'Would send {reminder.reminder_type} reminder for '
                            f'appointment {reminder.appointment.appointment_code}'
                        )
                        sent_count += 1
                    else:
                        # In a real implementation, this would integrate with
                        # SMS, email, or WhatsApp services
                        self.send_reminder(reminder)
                        sent_count += 1
                        
                except Exception as e:
                    logger.error(f'Failed to send reminder {reminder.id}: {str(e)}')
                    failed_count += 1
                    
                    if not dry_run:
                        reminder.delivery_status = 'failed'
                        reminder.error_message = str(e)
                        reminder.save()
            
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f'Dry run completed: {sent_count} reminders would be sent')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Reminders processed: {sent_count} sent, {failed_count} failed')
                )
                
        except Exception as e:
            logger.error(f'Command failed: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Command failed: {str(e)}')
            )
    
    def send_reminder(self, reminder):
        """Send a reminder via the appropriate channel."""
        # This is a placeholder implementation
        # In a real system, this would integrate with actual messaging services
        
        appointment = reminder.appointment
        message_template = reminder.message_template
        
        # Generate personalized message
        if isinstance(message_template, dict):
            message_en = message_template.get('en', '')
            message_ar = message_template.get('ar', '')
        else:
            message_en = str(message_template)
            message_ar = ''
        
        # Replace placeholders
        message_en = message_en.format(
            patient_name=appointment.patient.full_name,
            doctor_name=appointment.doctor.full_name,
            appointment_date=appointment.appointment_date.strftime('%Y-%m-%d'),
            appointment_time=appointment.appointment_time.strftime('%H:%M'),
            appointment_code=appointment.appointment_code
        )
        
        if message_ar:
            message_ar = message_ar.format(
                patient_name=appointment.patient.full_name_ar,
                doctor_name=appointment.doctor.full_name_ar,
                appointment_date=appointment.appointment_date.strftime('%Y-%m-%d'),
                appointment_time=appointment.appointment_time.strftime('%H:%M'),
                appointment_code=appointment.appointment_code
            )
        
        # Log the message (in real implementation, send via appropriate service)
        logger.info(f'Sending {reminder.reminder_type} reminder: {message_en}')
        
        # Mark as sent
        ReminderService.mark_reminder_sent(str(reminder.id), 'sent')
