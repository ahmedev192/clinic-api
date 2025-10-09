"""
Inventory filters
"""
import django_filters
from django.db.models import Q
from .models import Item, StockMovement, PurchaseOrder, MaintenanceRecord


class ItemFilter(django_filters.FilterSet):
    """Filter for Item model"""
    name = django_filters.CharFilter(method='filter_name')
    item_type = django_filters.ChoiceFilter(choices=Item.ITEM_TYPES)
    status = django_filters.ChoiceFilter(choices=Item.STATUS_CHOICES)
    condition = django_filters.ChoiceFilter(choices=Item.CONDITION_CHOICES)
    category = django_filters.NumberFilter(field_name='category__id')
    supplier = django_filters.NumberFilter(field_name='suppliers__id')
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')
    expired = django_filters.BooleanFilter(method='filter_expired')
    expiring_soon = django_filters.BooleanFilter(method='filter_expiring_soon')
    min_quantity = django_filters.NumberFilter(field_name='current_quantity', lookup_expr='gte')
    max_quantity = django_filters.NumberFilter(field_name='current_quantity', lookup_expr='lte')
    
    class Meta:
        model = Item
        fields = ['item_type', 'status', 'condition', 'category', 'supplier', 'low_stock', 'expired', 'expiring_soon']
    
    def filter_name(self, queryset, name, value):
        """Filter by name in both English and Arabic"""
        return queryset.filter(
            Q(name_en__icontains=value) | Q(name_ar__icontains=value)
        )
    
    def filter_low_stock(self, queryset, name, value):
        """Filter items with low stock"""
        if value:
            return queryset.filter(current_quantity__lte=models.F('reorder_level'))
        return queryset
    
    def filter_expired(self, queryset, name, value):
        """Filter expired items"""
        if value:
            from django.utils import timezone
            return queryset.filter(expiry_date__lt=timezone.now().date())
        return queryset
    
    def filter_expiring_soon(self, queryset, name, value):
        """Filter items expiring soon (within 30 days)"""
        if value:
            from django.utils import timezone
            from datetime import timedelta
            today = timezone.now().date()
            future_date = today + timedelta(days=30)
            return queryset.filter(
                expiry_date__gte=today,
                expiry_date__lte=future_date
            )
        return queryset


class StockMovementFilter(django_filters.FilterSet):
    """Filter for StockMovement model"""
    movement_type = django_filters.ChoiceFilter(choices=StockMovement.MOVEMENT_TYPES)
    item = django_filters.NumberFilter(field_name='item__id')
    user = django_filters.NumberFilter(field_name='user__id')
    department = django_filters.CharFilter(field_name='department', lookup_expr='icontains')
    date_from = django_filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created', lookup_expr='lte')
    
    class Meta:
        model = StockMovement
        fields = ['movement_type', 'item', 'user', 'department', 'date_from', 'date_to']


class PurchaseOrderFilter(django_filters.FilterSet):
    """Filter for PurchaseOrder model"""
    status = django_filters.ChoiceFilter(choices=PurchaseOrder.STATUS_CHOICES)
    supplier = django_filters.NumberFilter(field_name='supplier__id')
    created_by = django_filters.NumberFilter(field_name='created_by__id')
    approved_by = django_filters.NumberFilter(field_name='approved_by__id')
    date_from = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='lte')
    min_amount = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    
    class Meta:
        model = PurchaseOrder
        fields = ['status', 'supplier', 'created_by', 'approved_by', 'date_from', 'date_to', 'min_amount', 'max_amount']


class MaintenanceRecordFilter(django_filters.FilterSet):
    """Filter for MaintenanceRecord model"""
    maintenance_type = django_filters.ChoiceFilter(choices=MaintenanceRecord.MAINTENANCE_TYPES)
    status = django_filters.ChoiceFilter(choices=MaintenanceRecord.STATUS_CHOICES)
    item = django_filters.NumberFilter(field_name='item__id')
    created_by = django_filters.NumberFilter(field_name='created_by__id')
    scheduled_from = django_filters.DateTimeFilter(field_name='scheduled_date', lookup_expr='gte')
    scheduled_to = django_filters.DateTimeFilter(field_name='scheduled_date', lookup_expr='lte')
    completed_from = django_filters.DateTimeFilter(field_name='completed_date', lookup_expr='gte')
    completed_to = django_filters.DateTimeFilter(field_name='completed_date', lookup_expr='lte')
    due = django_filters.BooleanFilter(method='filter_due')
    
    class Meta:
        model = MaintenanceRecord
        fields = ['maintenance_type', 'status', 'item', 'created_by', 'scheduled_from', 'scheduled_to', 'due']
    
    def filter_due(self, queryset, name, value):
        """Filter maintenance records due for service"""
        if value:
            from django.utils import timezone
            return queryset.filter(
                next_maintenance_date__lte=timezone.now().date(),
                status__in=['scheduled', 'in_progress']
            )
        return queryset
