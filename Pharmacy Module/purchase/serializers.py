from rest_framework import serializers
from .models import Supplier, PurchaseOrder, PurchaseOrderItem
from medicine.serializers import MedicineSerializer


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model"""
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'email', 'phone', 'address',
            'is_active', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrderItem model"""
    medicine_name = serializers.CharField(source='medicine.name_en', read_only=True)
    medicine_name_ar = serializers.CharField(source='medicine.name_ar', read_only=True)
    medicine_internal_code = serializers.CharField(source='medicine.internal_code', read_only=True)
    is_fully_received = serializers.SerializerMethodField()
    remaining_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'medicine', 'medicine_name', 'medicine_name_ar', 'medicine_internal_code',
            'quantity', 'received_quantity', 'unit_cost', 'total_cost',
            'batch_number', 'expiration_date', 'notes',
            'is_fully_received', 'remaining_quantity',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'total_cost', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_fully_received', 'remaining_quantity']

    def get_is_fully_received(self, obj):
        """Check if item is fully received"""
        return obj.is_fully_received()

    def get_remaining_quantity(self, obj):
        """Get remaining quantity to be received"""
        return obj.get_remaining_quantity()


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrder model"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    received_items = serializers.SerializerMethodField()
    is_fully_received = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'supplier', 'supplier_name',
            'order_date', 'expected_delivery_date', 'actual_delivery_date',
            'status', 'subtotal', 'tax_amount', 'total_amount', 'notes',
            'total_items', 'received_items', 'is_fully_received',
            'items', 'created_at', 'updated_at', 'created_by', 'created_by_name', 'updated_by'
        ]
        read_only_fields = ['id', 'subtotal', 'total_amount', 'created_at', 'updated_at', 'created_by', 'updated_by', 'total_items', 'received_items', 'is_fully_received']

    def get_total_items(self, obj):
        """Get total number of items in the order"""
        return obj.get_total_items()

    def get_received_items(self, obj):
        """Get total number of received items"""
        return obj.get_received_items()

    def get_is_fully_received(self, obj):
        """Check if all items have been received"""
        return obj.is_fully_received()


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating purchase orders"""
    items = PurchaseOrderItemSerializer(many=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier', 'order_date', 'expected_delivery_date',
            'tax_amount', 'notes', 'items'
        ]

    def create(self, validated_data):
        """Create purchase order with items"""
        items_data = validated_data.pop('items')
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        
        for item_data in items_data:
            PurchaseOrderItem.objects.create(purchase_order=purchase_order, **item_data)
        
        # Calculate totals
        purchase_order.calculate_totals()
        
        return purchase_order


class PurchaseOrderItemReceiveSerializer(serializers.Serializer):
    """Serializer for receiving purchase order items"""
    received_quantity = serializers.IntegerField(min_value=1)
    batch_number = serializers.CharField(max_length=100)
    expiration_date = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_received_quantity(self, value):
        """Validate received quantity"""
        item = self.context['item']
        if value > item.get_remaining_quantity():
            raise serializers.ValidationError(
                f"Cannot receive more than remaining quantity. Remaining: {item.get_remaining_quantity()}"
            )
        return value


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for purchase order list views"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    total_items = serializers.SerializerMethodField()
    is_fully_received = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'supplier_name', 'order_date',
            'expected_delivery_date', 'status', 'total_amount',
            'total_items', 'is_fully_received', 'created_at'
        ]

    def get_total_items(self, obj):
        """Get total number of items in the order"""
        return obj.get_total_items()

    def get_is_fully_received(self, obj):
        """Check if all items have been received"""
        return obj.is_fully_received()
