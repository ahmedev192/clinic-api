from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import LabRequest, LabRequestItem
from apps.lab_tests.serializers import LabTestSerializer


class LabRequestItemSerializer(serializers.ModelSerializer):
    """Serializer for LabRequestItem model"""
    test_details = LabTestSerializer(source='test', read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = LabRequestItem
        fields = [
            'id', 'test', 'test_details', 'quantity', 'notes_en', 'notes_ar',
            'is_collected', 'is_completed', 'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LabRequestSerializer(serializers.ModelSerializer):
    """Serializer for LabRequest model"""
    items = LabRequestItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    urgency_display = serializers.CharField(source='get_urgency_display', read_only=True)
    
    class Meta:
        model = LabRequest
        fields = [
            'id', 'request_number', 'patient_id', 'patient_name', 'patient_name_ar',
            'doctor_id', 'doctor_name', 'doctor_name_ar', 'clinical_notes_en', 'clinical_notes_ar',
            'diagnosis_en', 'diagnosis_ar', 'status', 'status_display', 'urgency', 'urgency_display',
            'request_date', 'collection_date', 'completion_date', 'items', 'total_price',
            'created_by', 'updated_at'
        ]
        read_only_fields = ['id', 'request_number', 'request_date', 'updated_at', 'created_by']

    def get_total_price(self, obj):
        """Calculate total price for all items in the request"""
        return sum(item.total_price for item in obj.items.all())

    def create(self, validated_data):
        """Set the created_by field to the current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class LabRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating lab requests with items"""
    items = LabRequestItemSerializer(many=True)
    
    class Meta:
        model = LabRequest
        fields = [
            'patient_id', 'patient_name', 'patient_name_ar', 'doctor_id', 'doctor_name', 'doctor_name_ar',
            'clinical_notes_en', 'clinical_notes_ar', 'diagnosis_en', 'diagnosis_ar',
            'urgency', 'items'
        ]

    def create(self, validated_data):
        """Create lab request with items"""
        items_data = validated_data.pop('items')
        validated_data['created_by'] = self.context['request'].user
        
        request = LabRequest.objects.create(**validated_data)
        
        for item_data in items_data:
            LabRequestItem.objects.create(request=request, **item_data)
        
        return request


class LabRequestListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    urgency_display = serializers.CharField(source='get_urgency_display', read_only=True)
    items_count = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = LabRequest
        fields = [
            'id', 'request_number', 'patient_name', 'patient_name_ar', 'doctor_name', 'doctor_name_ar',
            'status', 'status_display', 'urgency', 'urgency_display', 'request_date',
            'items_count', 'total_price'
        ]
    
    def get_items_count(self, obj):
        """Get count of items in the request"""
        return obj.items.count()
    
    def get_total_price(self, obj):
        """Calculate total price for all items in the request"""
        return sum(item.total_price for item in obj.items.all())


class LabRequestStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating request status"""
    status = serializers.ChoiceField(choices=LabRequest.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)


class LabRequestItemStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating item status"""
    is_collected = serializers.BooleanField(required=False)
    is_completed = serializers.BooleanField(required=False)
    notes_en = serializers.CharField(required=False, allow_blank=True)
    notes_ar = serializers.CharField(required=False, allow_blank=True)
