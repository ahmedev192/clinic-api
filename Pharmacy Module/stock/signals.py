from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Stock, StockAlert, StockTransaction
from medicine.models import Medicine


@receiver(post_save, sender=Stock)
def check_stock_alerts(sender, instance, created, **kwargs):
    """Check and create stock alerts when stock is created or updated"""
    medicine = instance.medicine
    
    # Check for low stock alert
    if medicine.is_low_stock():
        StockAlert.objects.get_or_create(
            medicine=medicine,
            stock_record=instance,
            alert_type='low_stock',
            status='active',
            defaults={
                'message': f'Low stock alert: {medicine.name_en} has {instance.quantity} units remaining (reorder level: {medicine.reorder_level})',
                'threshold_value': medicine.reorder_level,
                'actual_value': instance.quantity,
            }
        )
    
    # Check for expiring soon alert
    if instance.is_expiring_soon(30):  # 30 days
        StockAlert.objects.get_or_create(
            medicine=medicine,
            stock_record=instance,
            alert_type='expiring_soon',
            status='active',
            defaults={
                'message': f'Expiring soon alert: {medicine.name_en} batch {instance.batch_number} expires on {instance.expiration_date}',
                'threshold_value': 30,
                'actual_value': instance.get_days_until_expiry(),
            }
        )
    
    # Check for expired alert
    if instance.is_expired():
        StockAlert.objects.get_or_create(
            medicine=medicine,
            stock_record=instance,
            alert_type='expired',
            status='active',
            defaults={
                'message': f'Expired alert: {medicine.name_en} batch {instance.batch_number} expired on {instance.expiration_date}',
                'threshold_value': 0,
                'actual_value': instance.get_days_until_expiry(),
            }
        )


@receiver(post_save, sender=StockTransaction)
def log_stock_transaction(sender, instance, created, **kwargs):
    """Log stock transactions for audit purposes"""
    if created:
        # This is handled in the views, but we can add additional logging here if needed
        pass
