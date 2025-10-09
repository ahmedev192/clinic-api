"""
Serializers for the Analytics module.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    ReportTemplate, ReportQuery, ReportResult, 
    DataSource, ReportSchedule
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ReportTemplate model."""
    created_by = UserSerializer(read_only=True)
    created_by_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'name_ar', 'description', 'description_ar',
            'report_type', 'modules', 'filters', 'date_range',
            'aggregation_fields', 'group_by_fields', 'export_formats',
            'include_charts', 'created_by', 'created_by_id',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_modules(self, value):
        """Validate that modules list contains valid module names."""
        valid_modules = ['patients', 'appointments', 'billing', 'doctors', 'consultations', 'insurance']
        for module in value:
            if module not in valid_modules:
                raise serializers.ValidationError(f"Invalid module: {module}")
        return value
    
    def validate_export_formats(self, value):
        """Validate export formats."""
        valid_formats = ['csv', 'excel', 'pdf']
        for format_type in value:
            if format_type not in valid_formats:
                raise serializers.ValidationError(f"Invalid export format: {format_type}")
        return value


class ReportQuerySerializer(serializers.ModelSerializer):
    """Serializer for ReportQuery model."""
    created_by = UserSerializer(read_only=True)
    created_by_id = serializers.IntegerField(write_only=True)
    template = ReportTemplateSerializer(read_only=True)
    template_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = ReportQuery
        fields = [
            'id', 'template', 'template_id', 'name', 'name_ar',
            'report_type', 'filters', 'date_from', 'date_to',
            'group_by', 'aggregation', 'status', 'created_by',
            'created_by_id', 'created_at', 'started_at',
            'completed_at', 'error_message', 'retry_count'
        ]
        read_only_fields = ['created_at', 'started_at', 'completed_at', 'status', 'error_message', 'retry_count']
    
    def validate_date_from(self, value):
        """Validate date_from is not in the future."""
        from django.utils import timezone
        if value > timezone.now():
            raise serializers.ValidationError("Date from cannot be in the future.")
        return value
    
    def validate_date_to(self, value):
        """Validate date_to is not in the future."""
        from django.utils import timezone
        if value > timezone.now():
            raise serializers.ValidationError("Date to cannot be in the future.")
        return value
    
    def validate(self, data):
        """Validate that date_from is before date_to."""
        if 'date_from' in data and 'date_to' in data:
            if data['date_from'] >= data['date_to']:
                raise serializers.ValidationError("Date from must be before date to.")
        return data


class ReportResultSerializer(serializers.ModelSerializer):
    """Serializer for ReportResult model."""
    query = ReportQuerySerializer(read_only=True)
    
    class Meta:
        model = ReportResult
        fields = [
            'id', 'query', 'data', 'summary', 'metadata',
            'csv_file', 'excel_file', 'pdf_file', 'cache_key',
            'expires_at', 'created_at'
        ]
        read_only_fields = ['created_at']


class DataSourceSerializer(serializers.ModelSerializer):
    """Serializer for DataSource model."""
    class Meta:
        model = DataSource
        fields = [
            'id', 'name', 'name_ar', 'source_type', 'connection_config',
            'is_active', 'last_sync', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_sync']
    
    def validate_connection_config(self, value):
        """Validate connection configuration based on source type."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Connection config must be a dictionary.")
        return value


class ReportScheduleSerializer(serializers.ModelSerializer):
    """Serializer for ReportSchedule model."""
    created_by = UserSerializer(read_only=True)
    created_by_id = serializers.IntegerField(write_only=True)
    template = ReportTemplateSerializer(read_only=True)
    template_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'template', 'template_id', 'name', 'name_ar',
            'frequency', 'time', 'recipients', 'is_active',
            'created_by', 'created_by_id', 'created_at',
            'last_run', 'next_run'
        ]
        read_only_fields = ['created_at', 'last_run', 'next_run']
    
    def validate_recipients(self, value):
        """Validate email recipients."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Recipients must be a list.")
        
        for email in value:
            if not isinstance(email, str) or '@' not in email:
                raise serializers.ValidationError(f"Invalid email address: {email}")
        return value


class FinancialReportSerializer(serializers.Serializer):
    """Serializer for financial report data."""
    date_from = serializers.DateTimeField()
    date_to = serializers.DateTimeField()
    department = serializers.CharField(required=False, allow_blank=True)
    payment_type = serializers.CharField(required=False, allow_blank=True)
    
    def validate_date_from(self, value):
        """Validate date_from is not in the future."""
        from django.utils import timezone
        if value > timezone.now():
            raise serializers.ValidationError("Date from cannot be in the future.")
        return value
    
    def validate_date_to(self, value):
        """Validate date_to is not in the future."""
        from django.utils import timezone
        if value > timezone.now():
            raise serializers.ValidationError("Date to cannot be in the future.")
        return value
    
    def validate(self, data):
        """Validate that date_from is before date_to."""
        if data['date_from'] >= data['date_to']:
            raise serializers.ValidationError("Date from must be before date to.")
        return data


class DemographicReportSerializer(serializers.Serializer):
    """Serializer for demographic report data."""
    date_from = serializers.DateTimeField()
    date_to = serializers.DateTimeField()
    include_gender = serializers.BooleanField(default=True)
    include_age_groups = serializers.BooleanField(default=True)
    include_location = serializers.BooleanField(default=True)
    include_visit_frequency = serializers.BooleanField(default=True)


class DoctorPerformanceSerializer(serializers.Serializer):
    """Serializer for doctor performance report data."""
    date_from = serializers.DateTimeField()
    date_to = serializers.DateTimeField()
    doctor_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    include_revenue = serializers.BooleanField(default=True)
    include_consultation_time = serializers.BooleanField(default=True)
    include_satisfaction = serializers.BooleanField(default=False)


class AppointmentStatsSerializer(serializers.Serializer):
    """Serializer for appointment statistics report data."""
    date_from = serializers.DateTimeField()
    date_to = serializers.DateTimeField()
    group_by = serializers.ChoiceField(
        choices=['day', 'week', 'month'],
        default='day'
    )
    include_no_shows = serializers.BooleanField(default=True)
    include_cancellations = serializers.BooleanField(default=True)
    include_peak_hours = serializers.BooleanField(default=True)


class CustomReportSerializer(serializers.Serializer):
    """Serializer for custom report builder."""
    name = serializers.CharField(max_length=200)
    name_ar = serializers.CharField(max_length=200, required=False, allow_blank=True)
    modules = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'patients', 'appointments', 'billing', 'doctors', 'consultations', 'insurance'
        ])
    )
    filters = serializers.DictField(required=False, default=dict)
    date_from = serializers.DateTimeField()
    date_to = serializers.DateTimeField()
    group_by_fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    aggregation_fields = serializers.DictField(required=False, default=dict)
    export_formats = serializers.ListField(
        child=serializers.ChoiceField(choices=['csv', 'excel', 'pdf']),
        default=['csv']
    )
    save_template = serializers.BooleanField(default=False)
    
    def validate_date_from(self, value):
        """Validate date_from is not in the future."""
        from django.utils import timezone
        if value > timezone.now():
            raise serializers.ValidationError("Date from cannot be in the future.")
        return value
    
    def validate_date_to(self, value):
        """Validate date_to is not in the future."""
        from django.utils import timezone
        if value > timezone.now():
            raise serializers.ValidationError("Date to cannot be in the future.")
        return value
    
    def validate(self, data):
        """Validate that date_from is before date_to."""
        if data['date_from'] >= data['date_to']:
            raise serializers.ValidationError("Date from must be before date to.")
        return data


class ExportRequestSerializer(serializers.Serializer):
    """Serializer for export requests."""
    query_id = serializers.IntegerField()
    format = serializers.ChoiceField(choices=['csv', 'excel', 'pdf'])
    include_headers_ar = serializers.BooleanField(default=True)
    include_headers_en = serializers.BooleanField(default=True)
    
    def validate_query_id(self, value):
        """Validate that the query exists and is completed."""
        try:
            query = ReportQuery.objects.get(id=value)
            if query.status != 'completed':
                raise serializers.ValidationError("Query must be completed before export.")
        except ReportQuery.DoesNotExist:
            raise serializers.ValidationError("Query not found.")
        return value
