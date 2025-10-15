"""
Utility functions for billing operations.
"""

from django.utils import timezone
from django.db import transaction, models
from decimal import Decimal
from .models import Invoice, InvoiceItem, Payment, Refund, AuditLog


def create_audit_log(action_type, user, description_en, description_ar, 
                    invoice=None, payment=None, refund=None, discount=None,
                    old_values=None, new_values=None, request=None):
    """Create an audit log entry."""
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    return AuditLog.objects.create(
        action_type=action_type,
        user=user,
        description_en=description_en,
        description_ar=description_ar,
        invoice=invoice,
        payment=payment,
        refund=refund,
        discount=discount,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent
    )


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def calculate_invoice_totals(invoice):
    """Calculate totals for an invoice."""
    # Calculate subtotal from items
    subtotal = sum(item.total_amount for item in invoice.items.all())
    invoice.subtotal = subtotal
    
    # Calculate tax amount
    invoice.tax_amount = (subtotal * invoice.tax_rate) / 100
    
    # Calculate total amount
    invoice.total_amount = subtotal + invoice.tax_amount - invoice.discount_amount
    
    # Update outstanding amount
    invoice.outstanding_amount = invoice.total_amount - invoice.paid_amount


def process_payment(invoice, payment_method, amount, reference_number='', 
                   notes_en='', notes_ar='', user=None):
    """Process a payment for an invoice."""
    with transaction.atomic():
        # Create payment
        payment = Payment.objects.create(
            invoice=invoice,
            payment_method=payment_method,
            amount=amount,
            reference_number=reference_number,
            notes_en=notes_en,
            notes_ar=notes_ar,
            payment_date=timezone.now(),
            created_by=user
        )
        
        # Update invoice paid amount
        invoice.paid_amount = sum(p.amount for p in invoice.payments.filter(is_verified=True))
        invoice.outstanding_amount = invoice.total_amount - invoice.paid_amount
        
        # Update invoice status
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = Invoice.INVOICE_STATUS.paid
        elif invoice.paid_amount > 0:
            invoice.status = Invoice.INVOICE_STATUS.pending
        
        invoice.save()
        
        # Create audit log
        create_audit_log(
            action_type=AuditLog.ACTION_TYPES.payment_created,
            user=user,
            description_en=f"Payment of {amount} processed for invoice {invoice.invoice_number}",
            description_ar=f"تم معالجة دفعة بقيمة {amount} للفاتورة {invoice.invoice_number}",
            invoice=invoice,
            payment=payment
        )
        
        return payment


def process_refund(invoice, amount, reason_en, reason_ar, notes_en='', notes_ar='', user=None):
    """Process a refund for an invoice."""
    with transaction.atomic():
        # Create refund
        refund = Refund.objects.create(
            invoice=invoice,
            amount=amount,
            reason_en=reason_en,
            reason_ar=reason_ar,
            notes_en=notes_en,
            notes_ar=notes_ar,
            status=Refund.REFUND_STATUS.pending,
            created_by=user
        )
        
        # Create audit log
        create_audit_log(
            action_type=AuditLog.ACTION_TYPES.refund_created,
            user=user,
            description_en=f"Refund of {amount} requested for invoice {invoice.invoice_number}",
            description_ar=f"تم طلب استرداد بقيمة {amount} للفاتورة {invoice.invoice_number}",
            invoice=invoice,
            refund=refund
        )
        
        return refund


def generate_invoice_number():
    """Generate a unique invoice number."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"INV-{timestamp}"


def generate_refund_number():
    """Generate a unique refund number."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"REF-{timestamp}"


def get_financial_summary(start_date, end_date):
    """Get financial summary for a date range."""
    invoices = Invoice.objects.filter(
        invoice_date__date__range=[start_date, end_date]
    )
    
    summary = {
        'total_invoices': invoices.count(),
        'total_revenue': invoices.aggregate(total=models.Sum('total_amount'))['total'] or Decimal('0'),
        'total_paid': invoices.aggregate(total=models.Sum('paid_amount'))['total'] or Decimal('0'),
        'total_outstanding': invoices.aggregate(total=models.Sum('outstanding_amount'))['total'] or Decimal('0'),
        'total_discounts': invoices.aggregate(total=models.Sum('discount_amount'))['total'] or Decimal('0'),
    }
    
    # Add refunds
    refunds = Refund.objects.filter(
        created__date__range=[start_date, end_date],
        status=Refund.REFUND_STATUS.processed
    )
    summary['total_refunds'] = refunds.aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
    
    return summary


def validate_invoice_data(data):
    """Validate invoice data before creation."""
    errors = []
    
    # Check required fields
    required_fields = ['patient', 'doctor', 'items']
    for field in required_fields:
        if field not in data:
            errors.append(f"{field} is required")
    
    # Validate items
    if 'items' in data:
        if not data['items']:
            errors.append("At least one item is required")
        
        for item in data['items']:
            if 'service' not in item:
                errors.append("Service is required for each item")
            if 'quantity' not in item or item['quantity'] <= 0:
                errors.append("Valid quantity is required for each item")
            if 'unit_price' not in item or item['unit_price'] < 0:
                errors.append("Valid unit price is required for each item")
    
    return errors


def calculate_discount_amount(discount, invoice_amount):
    """Calculate discount amount for an invoice."""
    if not discount.is_valid:
        return Decimal('0')
    
    if discount.min_invoice_amount and invoice_amount < discount.min_invoice_amount:
        return Decimal('0')
    
    if discount.discount_type == Discount.DISCOUNT_TYPES.percentage:
        amount = (invoice_amount * discount.value) / 100
    else:  # fixed
        amount = discount.value
    
    if discount.max_discount_amount:
        amount = min(amount, discount.max_discount_amount)
    
    return min(amount, invoice_amount)
