from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import LabResult, ResultAttachment
from apps.lab_samples.serializers import SampleSerializer


class ResultAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for ResultAttachment model"""
    
    class Meta:
        model = ResultAttachment
        fields = [
            'id', 'file', 'file_name', 'file_type', 'file_size',
            'description_en', 'description_ar', 'uploaded_at', 'uploaded_by'
        ]
        read_only_fields = ['id', 'file_size', 'uploaded_at', 'uploaded_by']

    def create(self, validated_data):
        """Set the uploaded_by field to the current user"""
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class LabResultSerializer(serializers.ModelSerializer):
    """Serializer for LabResult model"""
    sample_details = SampleSerializer(source='sample', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    abnormality_display = serializers.CharField(source='get_abnormality_display', read_only=True)
    is_abnormal = serializers.ReadOnlyField()
    attachments = ResultAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = LabResult
        fields = [
            'id', 'sample', 'sample_details', 'measured_value', 'unit',
            'normal_range_min', 'normal_range_max', 'normal_range_text_en', 'normal_range_text_ar',
            'abnormality_flag', 'abnormality_display', 'is_critical', 'is_abnormal',
            'comments_en', 'comments_ar', 'interpretation_en', 'interpretation_ar',
            'status', 'status_display', 'is_approved', 'approved_by', 'approved_at',
            'rejection_reason_en', 'rejection_reason_ar', 'rejected_by', 'rejected_at',
            'created_at', 'updated_at', 'completed_at', 'created_by', 'attachments'
        ]
        read_only_fields = [
            'id', 'abnormality_flag', 'is_critical', 'is_abnormal', 'created_at', 
            'updated_at', 'completed_at', 'created_by', 'approved_at', 'rejected_at'
        ]

    def create(self, validated_data):
        """Set the created_by field to the current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class LabResultListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    test_name = serializers.CharField(source='sample.request_item.test.name_en', read_only=True)
    test_name_ar = serializers.CharField(source='sample.request_item.test.name_ar', read_only=True)
    patient_name = serializers.CharField(source='sample.request_item.request.patient_name', read_only=True)
    patient_name_ar = serializers.CharField(source='sample.request_item.request.patient_name_ar', read_only=True)
    sample_barcode = serializers.CharField(source='sample.barcode', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    abnormality_display = serializers.CharField(source='get_abnormality_display', read_only=True)
    is_abnormal = serializers.ReadOnlyField()
    
    class Meta:
        model = LabResult
        fields = [
            'id', 'sample_barcode', 'test_name', 'test_name_ar', 'patient_name', 'patient_name_ar',
            'measured_value', 'unit', 'abnormality_flag', 'abnormality_display', 'is_critical', 'is_abnormal',
            'status', 'status_display', 'is_approved', 'created_at', 'completed_at'
        ]


class LabResultCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating lab results"""
    
    class Meta:
        model = LabResult
        fields = [
            'sample', 'measured_value', 'unit', 'normal_range_min', 'normal_range_max',
            'normal_range_text_en', 'normal_range_text_ar', 'comments_en', 'comments_ar',
            'interpretation_en', 'interpretation_ar', 'status'
        ]

    def create(self, validated_data):
        """Create lab result and update sample status"""
        validated_data['created_by'] = self.context['request'].user
        
        # Set completion date if status is final
        if validated_data.get('status') == 'final':
            from django.utils import timezone
            validated_data['completed_at'] = timezone.now()
        
        result = super().create(validated_data)
        
        # Update sample status to completed
        result.sample.status = 'completed'
        result.sample.save()
        
        return result


class LabResultApprovalSerializer(serializers.Serializer):
    """Serializer for approving/rejecting lab results"""
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    rejection_reason_en = serializers.CharField(required=False, allow_blank=True)
    rejection_reason_ar = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['action'] == 'reject' and not (data.get('rejection_reason_en') or data.get('rejection_reason_ar')):
            raise serializers.ValidationError(_("Rejection reason is required when rejecting a result"))
        return data


class LabResultUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating lab results"""
    
    class Meta:
        model = LabResult
        fields = [
            'measured_value', 'unit', 'normal_range_min', 'normal_range_max',
            'normal_range_text_en', 'normal_range_text_ar', 'comments_en', 'comments_ar',
            'interpretation_en', 'interpretation_ar', 'status'
        ]

    def validate(self, data):
        """Prevent editing of approved results"""
        if self.instance and self.instance.is_approved:
            raise serializers.ValidationError(_("Cannot edit approved results"))
        return data


class LabResultSearchSerializer(serializers.Serializer):
    """Serializer for result search functionality"""
    query = serializers.CharField(max_length=200, help_text=_("Search term for patient name, barcode, or test name"))
    status = serializers.ChoiceField(choices=LabResult.STATUS_CHOICES, required=False)
    abnormality_flag = serializers.ChoiceField(choices=LabResult.ABNORMALITY_CHOICES, required=False)
    is_critical = serializers.BooleanField(required=False)
    is_approved = serializers.BooleanField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
