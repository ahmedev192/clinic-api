"""
Management command to generate inventory reports
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from inventory.utils import generate_inventory_report


class Command(BaseCommand):
    help = 'Generate inventory report'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date for report (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date for report (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path (optional)',
        )
    
    def handle(self, *args, **options):
        start_date = options.get('start_date')
        end_date = options.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = timezone.now().date() - timedelta(days=30)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()
        
        self.stdout.write(f'Generating report from {start_date} to {end_date}...')
        
        try:
            report = generate_inventory_report(start_date, end_date)
            
            if options.get('output'):
                # Save to file
                import json
                with open(options['output'], 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                self.stdout.write(
                    self.style.SUCCESS(f'Report saved to {options["output"]}')
                )
            else:
                # Print to console
                self.stdout.write('Inventory Report:')
                self.stdout.write('=' * 50)
                
                # Stock Summary
                stock = report['stock_summary']
                self.stdout.write('Stock Summary:')
                self.stdout.write(f'  Total Items: {stock["total_items"]}')
                self.stdout.write(f'  Active Items: {stock["active_items"]}')
                self.stdout.write(f'  Low Stock Items: {stock["low_stock_items"]}')
                self.stdout.write(f'  Total Value: ${stock["total_value"] or 0:.2f}')
                
                # Movements Summary
                movements = report['movements_summary']
                self.stdout.write('\nMovements Summary:')
                self.stdout.write(f'  Total Movements: {movements["total_movements"]}')
                self.stdout.write(f'  Total In: {movements["total_in"] or 0}')
                self.stdout.write(f'  Total Out: {movements["total_out"] or 0}')
                
                # Purchase Summary
                purchase = report['purchase_summary']
                self.stdout.write('\nPurchase Summary:')
                self.stdout.write(f'  Total Orders: {purchase["total_orders"]}')
                self.stdout.write(f'  Total Value: ${purchase["total_value"] or 0:.2f}')
                self.stdout.write(f'  Pending Orders: {purchase["pending_orders"]}')
                self.stdout.write(f'  Received Orders: {purchase["received_orders"]}')
                
                # Maintenance Summary
                maintenance = report['maintenance_summary']
                self.stdout.write('\nMaintenance Summary:')
                self.stdout.write(f'  Total Maintenance: {maintenance["total_maintenance"]}')
                self.stdout.write(f'  Completed: {maintenance["completed_maintenance"]}')
                self.stdout.write(f'  Pending: {maintenance["pending_maintenance"]}')
            
            self.stdout.write(
                self.style.SUCCESS('Report generated successfully')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating report: {e}')
            )
