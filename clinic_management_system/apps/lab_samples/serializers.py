from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Sample, SampleCollection
from apps.lab_requests.serializers import LabRequestItemSerializer


class SampleSerializer(serializers.ModelSerializer):
    """Serializer for Sample model"""
    request_item_details = LabRequestItemSerializer(source='request_item', read_only=True)
    is_expired = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sample_type_display = serializers.CharField(source='get_sample_type_display', read_only=True)
    
    class Meta:
        model = Sample
        fields = [
            'id', 'barcode', 'tracking_code', 'request_item', 'request_item_details',
            'sample_type', 'sample_type_display', 'volume', 'container_type',
            'collection_date', 'collector_name', 'collector_name_ar', 'collection_location',
            'status', 'status_display', 'storage_location', 'temperature',
            'collection_notes_en', 'collection_notes_ar', 'rejection_reason_en', 'rejection_reason_ar',
            'is_expired', 'days_until_expiry', 'expiry_date', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = [
            'id', 'barcode', 'tracking_code', 'created_at', 'updated_at', 'created_by'
        ]

    def create(self, validated_data):
        """Set the created_by field to the current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SampleListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    test_name = serializers.CharField(source='request_item.test.name_en', read_only=True)
    test_name_ar = serializers.CharField(source='request_item.test.name_ar', read_only=True)
    patient_name = serializers.CharField(source='request_item.request.patient_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sample_type_display = serializers.CharField(source='get_sample_type_display', read_only=True)
    
    class Meta:
        model = Sample
        fields = [
            'id', 'barcode', 'tracking_code', 'test_name', 'test_name_ar', 'patient_name',
            'sample_type', 'sample_type_display', 'status', 'status_display',
            'collection_date', 'collector_name', 'is_expired', 'created_at'
        ]


class SampleCollectionSerializer(serializers.ModelSerializer):
    """Serializer for SampleCollection model"""
    
    class Meta:
        model = SampleCollection
        fields = [
            'id', 'collection_batch_id', 'collection_date', 'collector_name', 'collector_name_ar',
            'location', 'total_samples', 'collected_samples', 'notes_en', 'notes_ar',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'collection_batch_id', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        """Set the created_by field to the current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SampleStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating sample status"""
    status = serializers.ChoiceField(choices=Sample.STATUS_CHOICES)
    storage_location = serializers.CharField(required=False, allow_blank=True)
    temperature = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    collection_notes_en = serializers.CharField(required=False, allow_blank=True)
    collection_notes_ar = serializers.CharField(required=False, allow_blank=True)
    rejection_reason_en = serializers.CharField(required=False, allow_blank=True)
    rejection_reason_ar = serializers.CharField(required=False, allow_blank=True)


class SampleCollectionUpdateSerializer(serializers.Serializer):
    """Serializer for updating sample collection"""
    collector_name = serializers.CharField(required=False, allow_blank=True)
    collector_name_ar = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    notes_en = serializers.CharField(required=False, allow_blank=True)
    notes_ar = serializers.CharField(required=False, allow_blank=True)


class SampleSearchSerializer(serializers.Serializer):
    """Serializer for sample search functionality"""
    query = serializers.CharField(max_length=200, help_text=_("Search term for barcode, tracking code, or patient name"))
    status = serializers.ChoiceField(choices=Sample.STATUS_CHOICES, required=False)
    sample_type = serializers.ChoiceField(choices=Sample.SAMPLE_TYPES, required=False)
    is_expired = serializers.BooleanField(required=False)
