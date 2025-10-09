from rest_framework import serializers
from .models import (
    ReportTemplate, GeneratedReport, AnalyticsMetric, 
    DashboardWidget, DataExport, ScheduledReport
)


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for report templates"""
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'report_type', 'report_type_display', 'description',
            'query_config', 'chart_config', 'filters', 'is_active',
            'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GeneratedReportSerializer(serializers.ModelSerializer):
    """Serializer for generated reports"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    generated_by_username = serializers.CharField(source='generated_by.username', read_only=True)
    
    class Meta:
        model = GeneratedReport
        fields = [
            'id', 'template', 'template_name', 'name', 'status', 'status_display',
            'parameters', 'data', 'file_path', 'generated_by', 'generated_by_username',
            'generated_at', 'completed_at', 'error_message'
        ]
        read_only_fields = ['id', 'generated_at', 'completed_at']


class AnalyticsMetricSerializer(serializers.ModelSerializer):
    """Serializer for analytics metrics"""
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    
    class Meta:
        model = AnalyticsMetric
        fields = [
            'id', 'metric_type', 'metric_type_display', 'name', 'value', 'unit',
            'period_start', 'period_end', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for dashboard widgets"""
    widget_type_display = serializers.CharField(source='get_widget_type_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'name', 'widget_type', 'widget_type_display', 'title',
            'description', 'data_source', 'configuration', 'position',
            'is_active', 'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DataExportSerializer(serializers.ModelSerializer):
    """Serializer for data exports"""
    export_type_display = serializers.CharField(source='get_export_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True)
    
    class Meta:
        model = DataExport
        fields = [
            'id', 'name', 'export_type', 'export_type_display', 'data_source',
            'filters', 'status', 'status_display', 'file_path', 'file_size',
            'requested_by', 'requested_by_username', 'requested_at', 'completed_at', 'error_message'
        ]
        read_only_fields = ['id', 'requested_at', 'completed_at']


class ScheduledReportSerializer(serializers.ModelSerializer):
    """Serializer for scheduled reports"""
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ScheduledReport
        fields = [
            'id', 'name', 'template', 'template_name', 'frequency', 'frequency_display',
            'parameters', 'recipients', 'is_active', 'last_run', 'next_run',
            'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_run', 'next_run']


class AnalyticsSummarySerializer(serializers.Serializer):
    """Serializer for analytics summary"""
    period = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_patients = serializers.IntegerField()
    total_appointments = serializers.IntegerField()
    total_consultations = serializers.IntegerField()
    average_appointment_duration = serializers.FloatField()
    patient_satisfaction_score = serializers.FloatField()
    staff_utilization_rate = serializers.FloatField()
    generated_at = serializers.DateTimeField()


class ChartDataSerializer(serializers.Serializer):
    """Serializer for chart data"""
    chart_type = serializers.CharField()
    title = serializers.CharField()
    data = serializers.JSONField()
    options = serializers.JSONField()
    generated_at = serializers.DateTimeField()


class KPISerializer(serializers.Serializer):
    """Serializer for KPI data"""
    name = serializers.CharField()
    value = serializers.CharField()
    unit = serializers.CharField()
    trend = serializers.CharField()
    trend_value = serializers.FloatField()
    color = serializers.CharField()
    icon = serializers.CharField()
