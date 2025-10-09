from rest_framework import serializers
from .models import Stock, StockAlert, StockTransaction
from medicine.serializers import MedicineSerializer


class StockSerializer(serializers.ModelSerializer):
    """Serializer for Stock model"""
    medicine_name = serializers.CharField(source='medicine.name_en', read_only=True)
    medicine_name_ar = serializers.CharField(source='medicine.name_ar', read_only=True)
    medicine_internal_code = serializers.CharField(source='medicine.internal_code', read_only=True)
    is_expired = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = Stock
        fields = [
            'id', 'medicine', 'medicine_name', 'medicine_name_ar', 'medicine_internal_code',
            'quantity', 'batch_number', 'expiration_date', 'purchase_cost', 'selling_price',
            'is_active', 'stock_type', 'purchase_order', 'notes',
            'is_expired', 'is_expiring_soon', 'days_until_expiry',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_expired', 'is_expiring_soon', 'days_until_expiry']

    def get_is_expired(self, obj):
        """Check if stock is expired"""
        return obj.is_expired()

    def get_is_expiring_soon(self, obj):
        """Check if stock is expiring soon"""
        return obj.is_expiring_soon()

    def get_days_until_expiry(self, obj):
        """Get days until expiry"""
        return obj.get_days_until_expiry()


class StockListSerializer(serializers.ModelSerializer):
    """Simplified serializer for stock list views"""
    medicine_name = serializers.CharField(source='medicine.name_en', read_only=True)
    medicine_internal_code = serializers.CharField(source='medicine.internal_code', read_only=True)
    is_expired = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    
    class Meta:
        model = Stock
        fields = [
            'id', 'medicine', 'medicine_name', 'medicine_internal_code',
            'quantity', 'batch_number', 'expiration_date', 'is_active',
            'is_expired', 'is_expiring_soon'
        ]

    def get_is_expired(self, obj):
        """Check if stock is expired"""
        return obj.is_expired()

    def get_is_expiring_soon(self, obj):
        """Check if stock is expiring soon"""
        return obj.is_expiring_soon()


class StockAlertSerializer(serializers.ModelSerializer):
    """Serializer for StockAlert model"""
    medicine_name = serializers.CharField(source='medicine.name_en', read_only=True)
    medicine_name_ar = serializers.CharField(source='medicine.name_ar', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'medicine', 'medicine_name', 'medicine_name_ar',
            'stock_record', 'alert_type', 'status', 'message',
            'threshold_value', 'actual_value', 'acknowledged_by', 'acknowledged_by_name',
            'acknowledged_at', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'acknowledged_by', 'acknowledged_at']

    def create(self, validated_data):
        """Create alert with current user as creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class StockTransactionSerializer(serializers.ModelSerializer):
    """Serializer for StockTransaction model"""
    medicine_name = serializers.CharField(source='medicine.name_en', read_only=True)
    medicine_name_ar = serializers.CharField(source='medicine.name_ar', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockTransaction
        fields = [
            'id', 'medicine', 'medicine_name', 'medicine_name_ar',
            'stock_record', 'transaction_type', 'quantity_change',
            'quantity_before', 'quantity_after', 'reference_number', 'reference_type',
            'notes', 'created_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']

    def create(self, validated_data):
        """Create transaction with current user as creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class StockAdjustmentSerializer(serializers.Serializer):
    """Serializer for stock adjustment operations"""
    medicine = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.filter(is_active=True))
    quantity_change = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)
    reference_number = serializers.CharField(required=False, allow_blank=True)
    reference_type = serializers.CharField(required=False, allow_blank=True)

    def validate_quantity_change(self, value):
        """Validate quantity change"""
        if value == 0:
            raise serializers.ValidationError("Quantity change cannot be zero")
        return value

    def validate(self, attrs):
        """Validate the adjustment"""
        medicine = attrs['medicine']
        quantity_change = attrs['quantity_change']
        
        # Check if we have enough stock for negative changes
        if quantity_change < 0 and abs(quantity_change) > medicine.quantity:
            raise serializers.ValidationError(
                f"Insufficient stock. Available: {medicine.quantity}, Requested: {abs(quantity_change)}"
            )
        
        return attrs
