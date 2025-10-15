"""
Django management command to cleanup old patient data.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.patient_management.models import Patient, PatientSearchLog


class Command(BaseCommand):
    help = 'Cleanup old patient data and search logs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days to keep data (default: 365)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f'Cleaning up data older than {days} days (before {cutoff_date.date()})')
        
        # Cleanup old search logs
        old_search_logs = PatientSearchLog.objects.filter(
            search_timestamp__lt=cutoff_date
        )
        
        search_logs_count = old_search_logs.count()
        if search_logs_count > 0:
            if dry_run:
                self.stdout.write(f'Would delete {search_logs_count} old search logs')
            else:
                old_search_logs.delete()
                self.stdout.write(f'Deleted {search_logs_count} old search logs')
        else:
            self.stdout.write('No old search logs found')
        
        # Cleanup old soft-deleted patients (older than 2 years)
        old_deleted_patients = Patient.objects.filter(
            is_deleted=True,
            deleted_at__lt=timezone.now() - timedelta(days=730)  # 2 years
        )
        
        deleted_patients_count = old_deleted_patients.count()
        if deleted_patients_count > 0:
            if dry_run:
                self.stdout.write(f'Would permanently delete {deleted_patients_count} old soft-deleted patients')
            else:
                old_deleted_patients.delete()
                self.stdout.write(f'Permanently deleted {deleted_patients_count} old soft-deleted patients')
        else:
            self.stdout.write('No old soft-deleted patients found')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No data was actually deleted'))
        else:
            self.stdout.write(self.style.SUCCESS('Cleanup completed successfully!'))
