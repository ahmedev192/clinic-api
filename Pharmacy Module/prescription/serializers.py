from rest_framework import serializers
from .models import Prescription, PrescriptionItem, DispensingRecord
from medicine.serializers import MedicineSerializer


class PrescriptionItemSerializer(serializers.ModelSerializer):
    """Serializer for PrescriptionItem model"""
    medicine_name = serializers.CharField(source='medicine.name_en', read_only=True)
    medicine_name_ar = serializers.CharField(source='medicine.name_ar', read_only=True)
    medicine_internal_code = serializers.CharField(source='medicine.internal_code', read_only=True)
    is_fully_dispensed = serializers.SerializerMethodField()
    remaining_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = PrescriptionItem
        fields = [
            'id', 'medicine', 'medicine_name', 'medicine_name_ar', 'medicine_internal_code',
            'quantity', 'dispensed_quantity', 'dosage_instructions_en', 'dosage_instructions_ar',
            'notes_en', 'notes_ar', 'is_fully_dispensed', 'remaining_quantity',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_fully_dispensed', 'remaining_quantity']

    def get_is_fully_dispensed(self, obj):
        """Check if item is fully dispensed"""
        return obj.is_fully_dispensed()

    def get_remaining_quantity(self, obj):
        """Get remaining quantity to be dispensed"""
        return obj.get_remaining_quantity()


class PrescriptionSerializer(serializers.ModelSerializer):
    """Serializer for Prescription model"""
    items = PrescriptionItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    dispensed_items = serializers.SerializerMethodField()
    is_fully_dispensed = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'consultation_id', 'prescription_number', 'patient_name', 'patient_id',
            'doctor_name', 'doctor_id', 'prescription_date', 'status',
            'notes_en', 'notes_ar', 'total_items', 'dispensed_items', 'is_fully_dispensed',
            'items', 'created_at', 'updated_at', 'created_by', 'created_by_name', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'total_items', 'dispensed_items', 'is_fully_dispensed']

    def get_total_items(self, obj):
        """Get total number of items in the prescription"""
        return obj.get_total_items()

    def get_dispensed_items(self, obj):
        """Get total number of dispensed items"""
        return obj.get_dispensed_items()

    def get_is_fully_dispensed(self, obj):
        """Check if all items have been dispensed"""
        return obj.is_fully_dispensed()


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating prescriptions"""
    items = PrescriptionItemSerializer(many=True)
    
    class Meta:
        model = Prescription
        fields = [
            'consultation_id', 'prescription_number', 'patient_name', 'patient_id',
            'doctor_name', 'doctor_id', 'prescription_date', 'notes_en', 'notes_ar', 'items'
        ]

    def create(self, validated_data):
        """Create prescription with items"""
        items_data = validated_data.pop('items')
        prescription = Prescription.objects.create(**validated_data)
        
        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)
        
        return prescription


class DispensingRecordSerializer(serializers.ModelSerializer):
    """Serializer for DispensingRecord model"""
    medicine_name = serializers.CharField(source='prescription_item.medicine.name_en', read_only=True)
    medicine_name_ar = serializers.CharField(source='prescription_item.medicine.name_ar', read_only=True)
    prescription_number = serializers.CharField(source='prescription_item.prescription.prescription_number', read_only=True)
    patient_name = serializers.CharField(source='prescription_item.prescription.patient_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = DispensingRecord
        fields = [
            'id', 'prescription_item', 'medicine_name', 'medicine_name_ar',
            'prescription_number', 'patient_name', 'quantity_dispensed',
            'dispensing_date', 'pharmacist_name', 'pharmacist_id',
            'stock_record', 'batch_number', 'notes_en', 'notes_ar',
            'created_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']

    def create(self, validated_data):
        """Create dispensing record with current user as creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class DispensingSerializer(serializers.Serializer):
    """Serializer for dispensing operations"""
    prescription_item = serializers.PrimaryKeyRelatedField(queryset=PrescriptionItem.objects.all())
    quantity_to_dispense = serializers.IntegerField(min_value=1)
    pharmacist_name = serializers.CharField(max_length=200)
    pharmacist_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    batch_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    notes_en = serializers.CharField(required=False, allow_blank=True)
    notes_ar = serializers.CharField(required=False, allow_blank=True)

    def validate_quantity_to_dispense(self, value):
        """Validate quantity to dispense"""
        prescription_item = self.initial_data.get('prescription_item')
        if prescription_item:
            remaining = prescription_item.get_remaining_quantity()
            if value > remaining:
                raise serializers.ValidationError(
                    f"Cannot dispense more than remaining quantity. Remaining: {remaining}"
                )
        return value

    def validate(self, attrs):
        """Validate the dispensing operation"""
        prescription_item = attrs['prescription_item']
        quantity_to_dispense = attrs['quantity_to_dispense']
        
        # Check if prescription item has remaining quantity
        if prescription_item.get_remaining_quantity() < quantity_to_dispense:
            raise serializers.ValidationError(
                f"Insufficient remaining quantity. Remaining: {prescription_item.get_remaining_quantity()}"
            )
        
        return attrs


class PrescriptionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for prescription list views"""
    total_items = serializers.SerializerMethodField()
    is_fully_dispensed = serializers.SerializerMethodField()
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'prescription_number', 'patient_name', 'doctor_name',
            'prescription_date', 'status', 'total_items', 'is_fully_dispensed', 'created_at'
        ]

    def get_total_items(self, obj):
        """Get total number of items in the prescription"""
        return obj.get_total_items()

    def get_is_fully_dispensed(self, obj):
        """Check if all items have been dispensed"""
        return obj.is_fully_dispensed()
