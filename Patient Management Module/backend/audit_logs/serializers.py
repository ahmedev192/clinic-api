"""
Audit Logging Serializers

This module provides serializers for audit log models.
"""

from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog, PatientAccessLog, DataExportLog, SystemEventLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'action', 'timestamp', 'user', 'user_name', 'user_full_name',
            'content_type', 'content_type_name', 'object_id', 'field_name',
            'old_value', 'new_value', 'description', 'ip_address', 'user_agent',
            'request_path', 'request_method', 'additional_data'
        ]
        read_only_fields = fields
    
    def get_user_full_name(self, obj):
        """Get user's full name"""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username


class PatientAccessLogSerializer(serializers.ModelSerializer):
    """Serializer for PatientAccessLog model"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    patient_code = serializers.CharField(source='patient.patient_code', read_only=True)
    patient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientAccessLog
        fields = [
            'id', 'patient', 'patient_code', 'patient_name', 'user', 'user_name',
            'user_full_name', 'access_type', 'timestamp', 'ip_address', 'user_agent',
            'request_path', 'reason', 'additional_data'
        ]
        read_only_fields = fields
    
    def get_user_full_name(self, obj):
        """Get user's full name"""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username
    
    def get_patient_name(self, obj):
        """Get patient's full name"""
        return obj.patient.get_full_name()


class DataExportLogSerializer(serializers.ModelSerializer):
    """Serializer for DataExportLog model"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = DataExportLog
        fields = [
            'id', 'user', 'user_name', 'user_full_name', 'export_type', 'format',
            'timestamp', 'record_count', 'file_size', 'file_size_display', 'file_path',
            'filters_applied', 'ip_address', 'user_agent'
        ]
        read_only_fields = fields
    
    def get_user_full_name(self, obj):
        """Get user's full name"""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username
    
    def get_file_size_display(self, obj):
        """Get human-readable file size"""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class SystemEventLogSerializer(serializers.ModelSerializer):
    """Serializer for SystemEventLog model"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True)
    resolved_by_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemEventLog
        fields = [
            'id', 'event_type', 'timestamp', 'user', 'user_name', 'user_full_name',
            'title', 'description', 'module', 'error_code', 'stack_trace', 'request_data',
            'is_resolved', 'resolved_by', 'resolved_by_name', 'resolved_by_full_name',
            'resolved_at', 'resolution_notes'
        ]
        read_only_fields = fields
    
    def get_user_full_name(self, obj):
        """Get user's full name"""
        if obj.user and obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username if obj.user else None
    
    def get_resolved_by_full_name(self, obj):
        """Get resolver's full name"""
        if obj.resolved_by and obj.resolved_by.first_name and obj.resolved_by.last_name:
            return f"{obj.resolved_by.first_name} {obj.resolved_by.last_name}"
        return obj.resolved_by.username if obj.resolved_by else None
