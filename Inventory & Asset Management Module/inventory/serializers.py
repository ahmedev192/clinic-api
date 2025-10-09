"""
Inventory serializers
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Category, Supplier, Item, StockMovement, PurchaseOrder, 
    PurchaseOrderItem, MaintenanceRecord, Alert
)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name_en', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'parent', 'parent_name', 'children', 'is_active', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_children(self, obj):
        """Get child categories"""
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model"""
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name_en', 'name_ar', 'contact_person', 'email', 'phone',
            'address_en', 'address_ar', 'notes_en', 'notes_ar', 'is_active',
            'items_count', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_items_count(self, obj):
        """Get count of items supplied by this supplier"""
        return obj.items.count()


class ItemSerializer(serializers.ModelSerializer):
    """Serializer for Item model"""
    category_name = serializers.CharField(source='category.name_en', read_only=True)
    primary_supplier_name = serializers.CharField(source='primary_supplier.name_en', read_only=True)
    suppliers_names = serializers.SerializerMethodField()
    is_low_stock = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Item
        fields = [
            'id', 'code', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'item_type', 'category', 'category_name', 'current_quantity', 'unit',
            'reorder_level', 'location', 'status', 'condition', 'primary_supplier',
            'primary_supplier_name', 'suppliers', 'suppliers_names', 'unit_cost',
            'barcode', 'serial_number', 'expiry_date', 'warranty_expiry',
            'is_low_stock', 'is_expired', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
    
    def get_suppliers_names(self, obj):
        """Get names of all suppliers for this item"""
        return [supplier.name_en for supplier in obj.suppliers.all()]


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for StockMovement model"""
    item_name = serializers.CharField(source='item.name_en', read_only=True)
    item_code = serializers.CharField(source='item.code', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'item', 'item_name', 'item_code', 'movement_type', 'movement_type_display',
            'quantity', 'previous_quantity', 'new_quantity', 'reference_number',
            'notes_en', 'notes_ar', 'user', 'user_name', 'department',
            'purchase_order', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrderItem model"""
    item_name = serializers.CharField(source='item.name_en', read_only=True)
    item_code = serializers.CharField(source='item.code', read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'item', 'item_name', 'item_code', 'quantity_ordered',
            'quantity_received', 'unit_price', 'total_price', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrder model"""
    supplier_name = serializers.CharField(source='supplier.name_en', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'supplier', 'supplier_name', 'status', 'status_display',
            'order_date', 'expected_delivery', 'actual_delivery', 'subtotal',
            'tax_amount', 'total_amount', 'notes_en', 'notes_ar', 'created_by',
            'created_by_name', 'approved_by', 'approved_by_name', 'approved_at',
            'items', 'created', 'modified'
        ]
        read_only_fields = ['id', 'order_number', 'created', 'modified']


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for MaintenanceRecord model"""
    item_name = serializers.CharField(source='item.name_en', read_only=True)
    item_code = serializers.CharField(source='item.code', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = MaintenanceRecord
        fields = [
            'id', 'item', 'item_name', 'item_code', 'maintenance_type',
            'maintenance_type_display', 'status', 'status_display', 'scheduled_date',
            'completed_date', 'next_maintenance_date', 'technician_name',
            'technician_contact', 'description_en', 'description_ar',
            'notes_en', 'notes_ar', 'cost', 'created_by', 'created_by_name',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model"""
    item_name = serializers.CharField(source='item.name_en', read_only=True)
    item_code = serializers.CharField(source='item.code', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'alert_type', 'alert_type_display', 'priority', 'priority_display',
            'item', 'item_name', 'item_code', 'maintenance_record', 'title_en',
            'title_ar', 'message_en', 'message_ar', 'is_read', 'is_resolved',
            'resolved_at', 'resolved_by', 'resolved_by_name', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


# Nested serializers for detailed views
class ItemDetailSerializer(ItemSerializer):
    """Detailed serializer for Item with related data"""
    movements = StockMovementSerializer(many=True, read_only=True)
    maintenance_records = MaintenanceRecordSerializer(many=True, read_only=True)
    alerts = AlertSerializer(many=True, read_only=True)


class PurchaseOrderDetailSerializer(PurchaseOrderSerializer):
    """Detailed serializer for PurchaseOrder with items"""
    items = PurchaseOrderItemSerializer(many=True, read_only=True)


# Serializers for integration APIs
class ItemIntegrationSerializer(serializers.ModelSerializer):
    """Simplified serializer for integration with other modules"""
    class Meta:
        model = Item
        fields = [
            'id', 'code', 'name_en', 'name_ar', 'item_type', 'current_quantity',
            'unit', 'unit_cost', 'status', 'location'
        ]


class StockMovementIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for stock movements in integration APIs"""
    item_code = serializers.CharField(source='item.code', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'item_code', 'movement_type', 'quantity', 'reference_number',
            'notes_en', 'notes_ar', 'department', 'created'
        ]
