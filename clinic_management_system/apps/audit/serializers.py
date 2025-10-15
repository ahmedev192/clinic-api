from rest_framework import serializers
from .models import (
    AuditLog, SystemLog, SecurityEvent, DataAccessLog, 
    ComplianceReport, AuditConfiguration
)


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs"""
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_username', 'action_type', 'action_type_display',
            'resource_type', 'resource_id', 'description', 'result', 'result_display',
            'ip_address', 'user_agent', 'request_path', 'request_method',
            'old_values', 'new_values', 'metadata', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class SystemLogSerializer(serializers.ModelSerializer):
    """Serializer for system logs"""
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    component_display = serializers.CharField(source='get_component_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SystemLog
        fields = [
            'id', 'level', 'level_display', 'component', 'component_display',
            'message', 'details', 'user', 'user_username', 'request_id',
            'ip_address', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class SecurityEventSerializer(serializers.ModelSerializer):
    """Serializer for security events"""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = SecurityEvent
        fields = [
            'id', 'event_type', 'event_type_display', 'severity', 'severity_display',
            'title', 'description', 'user', 'user_username', 'ip_address',
            'user_agent', 'request_path', 'is_resolved', 'resolved_at',
            'resolved_by', 'resolved_by_username', 'resolution_notes',
            'metadata', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp', 'resolved_at']


class DataAccessLogSerializer(serializers.ModelSerializer):
    """Serializer for data access logs"""
    access_type_display = serializers.CharField(source='get_access_type_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = DataAccessLog
        fields = [
            'id', 'user', 'user_username', 'access_type', 'access_type_display',
            'resource_type', 'resource_id', 'resource_name', 'ip_address',
            'user_agent', 'request_path', 'data_fields', 'purpose', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class ComplianceReportSerializer(serializers.ModelSerializer):
    """Serializer for compliance reports"""
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    generated_by_username = serializers.CharField(source='generated_by.username', read_only=True)
    
    class Meta:
        model = ComplianceReport
        fields = [
            'id', 'name', 'report_type', 'report_type_display', 'status', 'status_display',
            'period_start', 'period_end', 'generated_by', 'generated_by_username',
            'generated_at', 'file_path', 'file_size', 'summary', 'findings',
            'recommendations', 'metadata'
        ]
        read_only_fields = ['id', 'generated_at']


class AuditConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for audit configurations"""
    log_level_display = serializers.CharField(source='get_log_level_display', read_only=True)
    
    class Meta:
        model = AuditConfiguration
        fields = [
            'id', 'component', 'is_enabled', 'log_level', 'log_level_display',
            'retention_days', 'log_actions', 'exclude_users', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AuditSummarySerializer(serializers.Serializer):
    """Serializer for audit summary"""
    total_actions = serializers.IntegerField()
    actions_today = serializers.IntegerField()
    actions_this_week = serializers.IntegerField()
    actions_this_month = serializers.IntegerField()
    failed_actions = serializers.IntegerField()
    security_events = serializers.IntegerField()
    data_access_events = serializers.IntegerField()
    last_updated = serializers.DateTimeField()


class SecuritySummarySerializer(serializers.Serializer):
    """Serializer for security summary"""
    total_events = serializers.IntegerField()
    critical_events = serializers.IntegerField()
    high_events = serializers.IntegerField()
    medium_events = serializers.IntegerField()
    low_events = serializers.IntegerField()
    unresolved_events = serializers.IntegerField()
    events_today = serializers.IntegerField()
    last_updated = serializers.DateTimeField()


class ComplianceSummarySerializer(serializers.Serializer):
    """Serializer for compliance summary"""
    total_reports = serializers.IntegerField()
    pending_reports = serializers.IntegerField()
    completed_reports = serializers.IntegerField()
    failed_reports = serializers.IntegerField()
    reports_by_type = serializers.JSONField()
    last_updated = serializers.DateTimeField()
