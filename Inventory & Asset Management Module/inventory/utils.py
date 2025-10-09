"""
Inventory utility functions
"""
from django.utils import timezone
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta
from .models import Item, StockMovement, Alert, MaintenanceRecord


def generate_item_code(item_type, category_id):
    """Generate unique item code based on type and category"""
    prefix_map = {
        'supply': 'SUP',
        'equipment': 'EQP',
        'tool': 'TOL',
        'consumable': 'CON',
        'furniture': 'FUR'
    }
    
    prefix = prefix_map.get(item_type, 'ITM')
    timestamp = timezone.now().strftime('%y%m%d')
    
    # Get count of items with same prefix and date
    count = Item.objects.filter(
        code__startswith=f"{prefix}-{timestamp}"
    ).count() + 1
    
    return f"{prefix}-{timestamp}-{count:03d}"


def check_low_stock_alerts():
    """Check for low stock items and create alerts"""
    from django.db import models
    low_stock_items = Item.objects.filter(
        current_quantity__lte=models.F('reorder_level'),
        status='active'
    )
    
    for item in low_stock_items:
        # Check if alert already exists
        existing_alert = Alert.objects.filter(
            item=item,
            alert_type='low_stock',
            is_resolved=False
        ).exists()
        
        if not existing_alert:
            Alert.objects.create(
                alert_type='low_stock',
                priority='high',
                item=item,
                title_en=f'Low Stock Alert: {item.name_en}',
                title_ar=f'تنبيه مخزون منخفض: {item.name_ar}',
                message_en=f'Item {item.name_en} is below reorder level. Current: {item.current_quantity}, Reorder: {item.reorder_level}',
                message_ar=f'المادة {item.name_ar} أقل من مستوى إعادة الطلب. الحالي: {item.current_quantity}, إعادة الطلب: {item.reorder_level}'
            )


def check_expiry_alerts():
    """Check for expired and expiring items and create alerts"""
    today = timezone.now().date()
    
    # Check expired items
    expired_items = Item.objects.filter(
        expiry_date__lt=today,
        status='active'
    )
    
    for item in expired_items:
        existing_alert = Alert.objects.filter(
            item=item,
            alert_type='expired',
            is_resolved=False
        ).exists()
        
        if not existing_alert:
            Alert.objects.create(
                alert_type='expired',
                priority='critical',
                item=item,
                title_en=f'Expired Item: {item.name_en}',
                title_ar=f'مادة منتهية الصلاحية: {item.name_ar}',
                message_en=f'Item {item.name_en} has expired on {item.expiry_date}',
                message_ar=f'المادة {item.name_ar} منتهية الصلاحية في {item.expiry_date}'
            )
    
    # Check items expiring soon (within 30 days)
    future_date = today + timedelta(days=30)
    expiring_items = Item.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=future_date,
        status='active'
    )
    
    for item in expiring_items:
        existing_alert = Alert.objects.filter(
            item=item,
            alert_type='expiring_soon',
            is_resolved=False
        ).exists()
        
        if not existing_alert:
            days_until_expiry = (item.expiry_date - today).days
            Alert.objects.create(
                alert_type='expiring_soon',
                priority='medium',
                item=item,
                title_en=f'Item Expiring Soon: {item.name_en}',
                title_ar=f'مادة تنتهي قريباً: {item.name_ar}',
                message_en=f'Item {item.name_en} will expire in {days_until_expiry} days on {item.expiry_date}',
                message_ar=f'المادة {item.name_ar} ستنتهي خلال {days_until_expiry} يوم في {item.expiry_date}'
            )


def check_maintenance_alerts():
    """Check for maintenance due items and create alerts"""
    today = timezone.now().date()
    
    maintenance_due = MaintenanceRecord.objects.filter(
        next_maintenance_date__lte=today,
        status__in=['scheduled', 'in_progress']
    )
    
    for maintenance in maintenance_due:
        existing_alert = Alert.objects.filter(
            maintenance_record=maintenance,
            alert_type='maintenance_due',
            is_resolved=False
        ).exists()
        
        if not existing_alert:
            Alert.objects.create(
                alert_type='maintenance_due',
                priority='medium',
                maintenance_record=maintenance,
                title_en=f'Maintenance Due: {maintenance.item.name_en}',
                title_ar=f'صيانة مستحقة: {maintenance.item.name_ar}',
                message_en=f'Maintenance is due for {maintenance.item.name_en} on {maintenance.next_maintenance_date}',
                message_ar=f'الصيانة مستحقة لـ {maintenance.item.name_ar} في {maintenance.next_maintenance_date}'
            )


def generate_inventory_report(start_date=None, end_date=None):
    """Generate comprehensive inventory report"""
    from django.db import models
    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    if not end_date:
        end_date = timezone.now().date()
    
    # Stock levels summary
    stock_summary = Item.objects.aggregate(
        total_items=Count('id'),
        active_items=Count('id', filter=Q(status='active')),
        low_stock_items=Count('id', filter=Q(current_quantity__lte=models.F('reorder_level'))),
        total_value=Sum(models.F('current_quantity') * models.F('unit_cost'))
    )
    
    # Stock movements summary
    movements_summary = StockMovement.objects.filter(
        created__date__range=[start_date, end_date]
    ).aggregate(
        total_movements=Count('id'),
        total_in=Sum('quantity', filter=Q(movement_type='in')),
        total_out=Sum('quantity', filter=Q(movement_type='out')),
    )
    
    # Purchase orders summary
    purchase_summary = PurchaseOrder.objects.filter(
        order_date__date__range=[start_date, end_date]
    ).aggregate(
        total_orders=Count('id'),
        total_value=Sum('total_amount'),
        pending_orders=Count('id', filter=Q(status='ordered')),
        received_orders=Count('id', filter=Q(status='received')),
    )
    
    # Maintenance summary
    maintenance_summary = MaintenanceRecord.objects.filter(
        scheduled_date__date__range=[start_date, end_date]
    ).aggregate(
        total_maintenance=Count('id'),
        completed_maintenance=Count('id', filter=Q(status='completed')),
        pending_maintenance=Count('id', filter=Q(status='scheduled')),
    )
    
    return {
        'period': {
            'start_date': start_date,
            'end_date': end_date
        },
        'stock_summary': stock_summary,
        'movements_summary': movements_summary,
        'purchase_summary': purchase_summary,
        'maintenance_summary': maintenance_summary
    }


def get_dashboard_data():
    """Get data for inventory dashboard"""
    from django.db import models
    today = timezone.now().date()
    
    # Quick stats
    stats = {
        'total_items': Item.objects.count(),
        'active_items': Item.objects.filter(status='active').count(),
        'low_stock_items': Item.objects.filter(
            current_quantity__lte=models.F('reorder_level'),
            status='active'
        ).count(),
        'expired_items': Item.objects.filter(
            expiry_date__lt=today,
            status='active'
        ).count(),
        'pending_orders': PurchaseOrder.objects.filter(status='ordered').count(),
        'maintenance_due': MaintenanceRecord.objects.filter(
            next_maintenance_date__lte=today,
            status__in=['scheduled', 'in_progress']
        ).count(),
        'unread_alerts': Alert.objects.filter(is_read=False).count(),
    }
    
    # Recent activities
    recent_movements = StockMovement.objects.select_related('item', 'user').order_by('-created')[:10]
    recent_alerts = Alert.objects.select_related('item').filter(is_resolved=False).order_by('-created')[:10]
    
    return {
        'stats': stats,
        'recent_movements': recent_movements,
        'recent_alerts': recent_alerts
    }
