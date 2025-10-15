"""
Django management command to cleanup old appointment data.

This command removes old audit logs and completed appointments based on retention policies.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from appointments.models import AppointmentAuditLog, Appointment
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to cleanup old appointment data."""
    
    help = 'Cleanup old appointment data based on retention policies'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--audit-log-days',
            type=int,
            default=365,
            help='Days to keep audit logs (default: 365)',
        )
        parser.add_argument(
            '--completed-appointments-days',
            type=int,
            default=1095,  # 3 years
            help='Days to keep completed appointments (default: 1095)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        audit_log_days = options['audit_log_days']
        completed_appointments_days = options['completed_appointments_days']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting cleanup (audit logs: {audit_log_days} days, '
                f'completed appointments: {completed_appointments_days} days, '
                f'dry-run: {dry_run})'
            )
        )
        
        try:
            # Cleanup audit logs
            audit_cutoff = timezone.now() - timedelta(days=audit_log_days)
            old_audit_logs = AppointmentAuditLog.objects.filter(timestamp__lt=audit_cutoff)
            
            if dry_run:
                self.stdout.write(f'Would delete {old_audit_logs.count()} old audit logs')
            else:
                deleted_audit_logs = old_audit_logs.count()
                old_audit_logs.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Deleted {deleted_audit_logs} old audit logs')
                )
            
            # Cleanup old completed appointments
            completed_cutoff = timezone.now() - timedelta(days=completed_appointments_days)
            old_completed_appointments = Appointment.objects.filter(
                status='completed',
                updated_at__lt=completed_cutoff
            )
            
            if dry_run:
                self.stdout.write(f'Would delete {old_completed_appointments.count()} old completed appointments')
            else:
                deleted_appointments = old_completed_appointments.count()
                old_completed_appointments.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Deleted {deleted_appointments} old completed appointments')
                )
            
            if dry_run:
                self.stdout.write(self.style.SUCCESS('Dry run completed'))
            else:
                self.stdout.write(self.style.SUCCESS('Cleanup completed successfully'))
                
        except Exception as e:
            logger.error(f'Cleanup command failed: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Cleanup failed: {str(e)}')
            )
