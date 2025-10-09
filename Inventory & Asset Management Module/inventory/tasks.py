"""
Celery tasks for inventory management
"""
from celery import shared_task
from django.utils import timezone
from .utils import check_low_stock_alerts, check_expiry_alerts, check_maintenance_alerts
from .models import Item, Alert


@shared_task
def check_inventory_alerts():
    """Check all inventory alerts and create new ones if needed"""
    try:
        check_low_stock_alerts()
        check_expiry_alerts()
        check_maintenance_alerts()
        return "Inventory alerts checked successfully"
    except Exception as e:
        return f"Error checking inventory alerts: {str(e)}"


@shared_task
def cleanup_old_alerts():
    """Clean up old resolved alerts (older than 30 days)"""
    try:
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_count = Alert.objects.filter(
            is_resolved=True,
            resolved_at__lt=cutoff_date
        ).delete()[0]
        
        return f"Cleaned up {deleted_count} old alerts"
    except Exception as e:
        return f"Error cleaning up alerts: {str(e)}"


@shared_task
def update_item_status():
    """Update item status based on various conditions"""
    try:
        today = timezone.now().date()
        
        # Mark expired items as inactive
        expired_items = Item.objects.filter(
            expiry_date__lt=today,
            status='active'
        )
        expired_count = expired_items.update(status='inactive')
        
        # Mark items under maintenance as active if maintenance is completed
        maintenance_items = Item.objects.filter(
            status='maintenance',
            maintenance_records__status='completed',
            maintenance_records__completed_date__isnull=False
        ).distinct()
        maintenance_count = maintenance_items.update(status='active')
        
        return f"Updated {expired_count} expired items and {maintenance_count} maintenance items"
    except Exception as e:
        return f"Error updating item status: {str(e)}"


@shared_task
def generate_daily_report():
    """Generate daily inventory report"""
    try:
        from .utils import generate_inventory_report
        from datetime import date
        
        today = date.today()
        yesterday = today - timezone.timedelta(days=1)
        
        report = generate_inventory_report(yesterday, today)
        
        # Here you could send the report via email or save to file
        # For now, just return the report data
        return f"Daily report generated for {today}"
    except Exception as e:
        return f"Error generating daily report: {str(e)}"
