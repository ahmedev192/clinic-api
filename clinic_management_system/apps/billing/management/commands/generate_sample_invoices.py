"""
Management command to generate sample invoices for testing.
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from apps.billing.models import (
    Patient, Doctor, Service, Invoice, InvoiceItem, PaymentMethod, Payment
)


class Command(BaseCommand):
    help = 'Generate sample invoices for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of sample invoices to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Generating {count} sample invoices...')
        
        # Get sample data
        patients = list(Patient.objects.all())
        doctors = list(Doctor.objects.all())
        services = list(Service.objects.all())
        payment_methods = list(PaymentMethod.objects.all())
        
        if not patients or not doctors or not services or not payment_methods:
            self.stdout.write(
                self.style.ERROR('Please run seed_data command first to create sample data')
            )
            return
        
        admin_user = User.objects.get(username='admin')
        
        # Generate invoices
        for i in range(count):
            # Select random data
            patient = patients[i % len(patients)]
            doctor = doctors[i % len(doctors)]
            
            # Create invoice
            invoice = Invoice.objects.create(
                patient=patient,
                doctor=doctor,
                visit_reference=f'VISIT-{i+1:04d}',
                tax_rate=15.0,  # 15% VAT
                invoice_date=timezone.now() - timedelta(days=i),
                due_date=timezone.now() + timedelta(days=30-i),
                notes_en=f'Sample invoice {i+1}',
                notes_ar=f'فاتورة تجريبية {i+1}',
                created_by=admin_user
            )
            
            # Generate invoice number
            invoice.invoice_number = f'INV-{invoice.id.hex[:8].upper()}'
            
            # Add 1-3 random services
            num_items = (i % 3) + 1
            selected_services = services[:num_items]
            
            for j, service in enumerate(selected_services):
                quantity = (j % 2) + 1
                unit_price = service.base_price
                discount_percentage = 0 if i % 4 == 0 else (i % 3) * 5  # 0%, 5%, or 10%
                
                InvoiceItem.objects.create(
                    invoice=invoice,
                    service=service,
                    description_en=service.name_en,
                    description_ar=service.name_ar,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount_percentage=discount_percentage,
                    service_reference=f'SVC-{i+1}-{j+1}',
                    notes_en=f'Item {j+1} for invoice {i+1}',
                    notes_ar=f'عنصر {j+1} للفاتورة {i+1}'
                )
            
            # Calculate totals
            invoice.calculate_totals()
            invoice.save()
            
            # Add payment for some invoices
            if i % 3 != 0:  # Skip every 3rd invoice (leave unpaid)
                payment_method = payment_methods[i % len(payment_methods)]
                payment_amount = invoice.total_amount if i % 4 == 0 else invoice.total_amount * Decimal('0.5')
                
                payment = Payment.objects.create(
                    invoice=invoice,
                    payment_method=payment_method,
                    amount=payment_amount,
                    reference_number=f'PAY-{i+1:04d}',
                    payment_date=invoice.invoice_date + timedelta(hours=1),
                    notes_en=f'Payment for invoice {invoice.invoice_number}',
                    notes_ar=f'دفعة للفاتورة {invoice.invoice_number}',
                    is_verified=True,
                    verified_by=admin_user,
                    verified_at=timezone.now(),
                    created_by=admin_user
                )
                
                # Update invoice paid amount
                invoice.paid_amount = payment_amount
                invoice.outstanding_amount = invoice.total_amount - payment_amount
                if invoice.paid_amount >= invoice.total_amount:
                    invoice.status = Invoice.INVOICE_STATUS.paid
                else:
                    invoice.status = Invoice.INVOICE_STATUS.pending
                invoice.save()
            
            self.stdout.write(f'Created invoice: {invoice.invoice_number}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated {count} sample invoices!'))

