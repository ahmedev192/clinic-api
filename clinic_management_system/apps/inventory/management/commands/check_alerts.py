"""
Management command to check inventory alerts
"""
from django.core.management.base import BaseCommand
from inventory.utils import check_low_stock_alerts, check_expiry_alerts, check_maintenance_alerts


class Command(BaseCommand):
    help = 'Check inventory alerts and create new ones if needed'
    
    def handle(self, *args, **options):
        self.stdout.write('Checking inventory alerts...')
        
        try:
            check_low_stock_alerts()
            self.stdout.write(
                self.style.SUCCESS('Low stock alerts checked successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error checking low stock alerts: {e}')
            )
        
        try:
            check_expiry_alerts()
            self.stdout.write(
                self.style.SUCCESS('Expiry alerts checked successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error checking expiry alerts: {e}')
            )
        
        try:
            check_maintenance_alerts()
            self.stdout.write(
                self.style.SUCCESS('Maintenance alerts checked successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error checking maintenance alerts: {e}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('All alert checks completed')
        )
