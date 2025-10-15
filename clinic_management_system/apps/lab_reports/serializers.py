from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import LabReport, ReportTemplate, ReportDelivery
from apps.lab_requests.serializers import LabRequestListSerializer


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ReportTemplate model"""
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'template_content_en', 'template_content_ar', 'is_default', 'is_active',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        """Set the created_by field to the current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ReportDeliverySerializer(serializers.ModelSerializer):
    """Serializer for ReportDelivery model"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    delivery_method_display = serializers.CharField(source='get_delivery_method_display', read_only=True)
    
    class Meta:
        model = ReportDelivery
        fields = [
            'id', 'report', 'delivery_method', 'delivery_method_display', 'delivery_reference',
            'recipient_email', 'recipient_phone', 'recipient_name', 'recipient_name_ar',
            'status', 'status_display', 'sent_at', 'delivered_at', 'opened_at',
            'error_message', 'retry_count', 'created_at'
        ]
        read_only_fields = [
            'id', 'sent_at', 'delivered_at', 'opened_at', 'created_at'
        ]


class LabReportSerializer(serializers.ModelSerializer):
    """Serializer for LabReport model"""
    lab_request_details = LabRequestListSerializer(source='lab_request', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    current_title = serializers.ReadOnlyField()
    current_content = serializers.ReadOnlyField()
    deliveries = ReportDeliverySerializer(many=True, read_only=True)
    
    class Meta:
        model = LabReport
        fields = [
            'id', 'report_number', 'lab_request', 'lab_request_details',
            'title_en', 'title_ar', 'current_title', 'format', 'format_display',
            'content_en', 'content_ar', 'current_content', 'file_path', 'file_size',
            'status', 'status_display', 'is_public', 'generated_at', 'delivered_at',
            'created_at', 'updated_at', 'created_by', 'deliveries'
        ]
        read_only_fields = [
            'id', 'report_number', 'file_size', 'generated_at', 'delivered_at',
            'created_at', 'updated_at', 'created_by'
        ]

    def create(self, validated_data):
        """Set the created_by field to the current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class LabReportListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    patient_name = serializers.CharField(source='lab_request.patient_name', read_only=True)
    patient_name_ar = serializers.CharField(source='lab_request.patient_name_ar', read_only=True)
    doctor_name = serializers.CharField(source='lab_request.doctor_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    
    class Meta:
        model = LabReport
        fields = [
            'id', 'report_number', 'patient_name', 'patient_name_ar', 'doctor_name',
            'title_en', 'title_ar', 'format', 'format_display', 'status', 'status_display',
            'is_public', 'generated_at', 'created_at'
        ]


class LabReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating lab reports"""
    template_id = serializers.IntegerField(required=False, help_text=_("Template ID to use for generation"))
    
    class Meta:
        model = LabReport
        fields = [
            'lab_request', 'title_en', 'title_ar', 'format', 'content_en', 'content_ar',
            'is_public', 'template_id'
        ]

    def create(self, validated_data):
        """Create lab report and generate file if needed"""
        template_id = validated_data.pop('template_id', None)
        validated_data['created_by'] = self.context['request'].user
        
        # Set generated timestamp
        from django.utils import timezone
        validated_data['generated_at'] = timezone.now()
        validated_data['status'] = 'generated'
        
        report = super().create(validated_data)
        
        # Generate file if needed
        if report.format in ['pdf', 'html']:
            report.generate_file()
        
        return report


class LabReportGenerateSerializer(serializers.Serializer):
    """Serializer for generating reports from requests"""
    lab_request_id = serializers.IntegerField(help_text=_("Lab request ID to generate report for"))
    template_id = serializers.IntegerField(required=False, help_text=_("Template ID to use"))
    format = serializers.ChoiceField(choices=LabReport.FORMAT_CHOICES, default='pdf')
    is_public = serializers.BooleanField(default=False)


class LabReportDeliverySerializer(serializers.Serializer):
    """Serializer for delivering reports"""
    delivery_method = serializers.ChoiceField(choices=ReportDelivery.DELIVERY_METHOD_CHOICES)
    recipient_email = serializers.EmailField(required=False, allow_blank=True)
    recipient_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    recipient_name = serializers.CharField(max_length=200)
    recipient_name_ar = serializers.CharField(max_length=200)

    def validate(self, data):
        """Validate delivery method specific requirements"""
        method = data.get('delivery_method')
        
        if method == 'email' and not data.get('recipient_email'):
            raise serializers.ValidationError(_("Email is required for email delivery"))
        
        if method == 'sms' and not data.get('recipient_phone'):
            raise serializers.ValidationError(_("Phone number is required for SMS delivery"))
        
        return data


class LabReportSearchSerializer(serializers.Serializer):
    """Serializer for report search functionality"""
    query = serializers.CharField(max_length=200, help_text=_("Search term for report number, patient name, or title"))
    status = serializers.ChoiceField(choices=LabReport.STATUS_CHOICES, required=False)
    format = serializers.ChoiceField(choices=LabReport.FORMAT_CHOICES, required=False)
    is_public = serializers.BooleanField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
