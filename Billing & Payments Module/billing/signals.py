"""
Signal handlers for billing models.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Invoice, Payment, Refund, AuditLog


@receiver(post_save, sender=Invoice)
def invoice_post_save(sender, instance, created, **kwargs):
    """Handle invoice post-save events."""
    if created:
        # Generate invoice number if not set
        if not instance.invoice_number:
            instance.invoice_number = f"INV-{instance.id.hex[:8].upper()}"
            instance.save(update_fields=['invoice_number'])
        
        # Create audit log
        AuditLog.objects.create(
            action_type=AuditLog.ACTION_TYPES.invoice_created,
            user=instance.created_by,
            description_en=f"Invoice {instance.invoice_number} created",
            description_ar=f"تم إنشاء الفاتورة {instance.invoice_number}",
            invoice=instance
        )


@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    """Handle payment post-save events."""
    if created:
        # Update invoice paid amount
        invoice = instance.invoice
        invoice.paid_amount = sum(
            p.amount for p in invoice.payments.filter(is_verified=True)
        )
        invoice.outstanding_amount = invoice.total_amount - invoice.paid_amount
        
        # Update invoice status
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = Invoice.INVOICE_STATUS.paid
        elif invoice.paid_amount > 0:
            invoice.status = Invoice.INVOICE_STATUS.pending
        
        invoice.save(update_fields=['paid_amount', 'outstanding_amount', 'status'])
        
        # Create audit log
        AuditLog.objects.create(
            action_type=AuditLog.ACTION_TYPES.payment_created,
            user=instance.created_by,
            description_en=f"Payment of {instance.amount} recorded for invoice {invoice.invoice_number}",
            description_ar=f"تم تسجيل دفعة بقيمة {instance.amount} للفاتورة {invoice.invoice_number}",
            invoice=invoice,
            payment=instance
        )


@receiver(post_save, sender=Refund)
def refund_post_save(sender, instance, created, **kwargs):
    """Handle refund post-save events."""
    if created:
        # Create audit log
        AuditLog.objects.create(
            action_type=AuditLog.ACTION_TYPES.refund_created,
            user=instance.created_by,
            description_en=f"Refund of {instance.amount} requested for invoice {instance.invoice.invoice_number}",
            description_ar=f"تم طلب استرداد بقيمة {instance.amount} للفاتورة {instance.invoice.invoice_number}",
            invoice=instance.invoice,
            refund=instance
        )
