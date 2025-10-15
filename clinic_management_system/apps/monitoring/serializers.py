from rest_framework import serializers
from .models import (
    SystemHealth, ModuleConnectivity, SystemAlert, 
    PerformanceMetric, ErrorLog, HealthCheck
)


class SystemHealthSerializer(serializers.ModelSerializer):
    """Serializer for system health"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SystemHealth
        fields = [
            'id', 'component', 'status', 'status_display', 'message',
            'last_checked', 'response_time', 'metadata'
        ]
        read_only_fields = ['id', 'last_checked']


class ModuleConnectivitySerializer(serializers.ModelSerializer):
    """Serializer for module connectivity"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ModuleConnectivity
        fields = [
            'id', 'module_name', 'base_url', 'status', 'status_display',
            'last_checked', 'response_time', 'error_message', 'is_active'
        ]
        read_only_fields = ['id', 'last_checked']


class SystemAlertSerializer(serializers.ModelSerializer):
    """Serializer for system alerts"""
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = SystemAlert
        fields = [
            'id', 'alert_type', 'alert_type_display', 'priority', 'priority_display',
            'title', 'message', 'component', 'is_resolved', 'resolved_at',
            'resolved_by', 'resolved_by_username', 'created_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'resolved_at']


class PerformanceMetricSerializer(serializers.ModelSerializer):
    """Serializer for performance metrics"""
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    
    class Meta:
        model = PerformanceMetric
        fields = [
            'id', 'metric_type', 'metric_type_display', 'value', 'unit',
            'component', 'timestamp', 'metadata'
        ]
        read_only_fields = ['id', 'timestamp']


class ErrorLogSerializer(serializers.ModelSerializer):
    """Serializer for error logs"""
    error_type_display = serializers.CharField(source='get_error_type_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ErrorLog
        fields = [
            'id', 'error_type', 'error_type_display', 'error_code', 'message',
            'stack_trace', 'user', 'user_username', 'component', 'request_path',
            'request_method', 'timestamp', 'is_resolved', 'resolved_at', 'metadata'
        ]
        read_only_fields = ['id', 'timestamp', 'resolved_at']


class HealthCheckSerializer(serializers.ModelSerializer):
    """Serializer for health checks"""
    check_type_display = serializers.CharField(source='get_check_type_display', read_only=True)
    last_status_display = serializers.CharField(source='get_last_status_display', read_only=True)
    
    class Meta:
        model = HealthCheck
        fields = [
            'id', 'name', 'check_type', 'check_type_display', 'endpoint',
            'expected_status', 'timeout', 'interval', 'is_active', 'last_run',
            'last_status', 'last_status_display', 'last_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_run']


class SystemStatusSerializer(serializers.Serializer):
    """Serializer for overall system status"""
    overall_status = serializers.CharField()
    healthy_components = serializers.IntegerField()
    warning_components = serializers.IntegerField()
    critical_components = serializers.IntegerField()
    connected_modules = serializers.IntegerField()
    disconnected_modules = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    last_updated = serializers.DateTimeField()


class HealthCheckResultSerializer(serializers.Serializer):
    """Serializer for health check results"""
    check_name = serializers.CharField()
    status = serializers.CharField()
    response_time = serializers.FloatField()
    message = serializers.CharField()
    timestamp = serializers.DateTimeField()
