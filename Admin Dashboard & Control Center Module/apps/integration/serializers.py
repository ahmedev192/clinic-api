from rest_framework import serializers
from .models import (
    ModuleConnection, APICall, DataSync, SyncLog, 
    WebhookEndpoint, WebhookLog, IntegrationTest
)


class ModuleConnectionSerializer(serializers.ModelSerializer):
    """Serializer for module connections"""
    module_type_display = serializers.CharField(source='get_module_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    authentication_type_display = serializers.CharField(source='get_authentication_type_display', read_only=True)
    
    class Meta:
        model = ModuleConnection
        fields = [
            'id', 'name', 'module_type', 'module_type_display', 'base_url',
            'api_version', 'status', 'status_display', 'is_enabled', 'timeout',
            'retry_attempts', 'authentication_type', 'authentication_type_display',
            'auth_config', 'last_checked', 'last_error', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_checked']


class APICallSerializer(serializers.ModelSerializer):
    """Serializer for API calls"""
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    connection_name = serializers.CharField(source='connection.name', read_only=True)
    initiated_by_username = serializers.CharField(source='initiated_by.username', read_only=True)
    
    class Meta:
        model = APICall
        fields = [
            'id', 'connection', 'connection_name', 'endpoint', 'method', 'method_display',
            'status', 'status_display', 'request_data', 'response_data', 'status_code',
            'response_time', 'error_message', 'initiated_by', 'initiated_by_username', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class DataSyncSerializer(serializers.ModelSerializer):
    """Serializer for data syncs"""
    sync_type_display = serializers.CharField(source='get_sync_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_module_name = serializers.CharField(source='source_module.name', read_only=True)
    target_module_name = serializers.CharField(source='target_module.name', read_only=True)
    
    class Meta:
        model = DataSync
        fields = [
            'id', 'name', 'source_module', 'source_module_name', 'target_module',
            'target_module_name', 'sync_type', 'sync_type_display', 'status',
            'status_display', 'source_endpoint', 'target_endpoint', 'mapping_config',
            'schedule_config', 'is_enabled', 'last_sync', 'next_sync', 'sync_count',
            'error_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_sync', 'next_sync']


class SyncLogSerializer(serializers.ModelSerializer):
    """Serializer for sync logs"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sync_name = serializers.CharField(source='sync.name', read_only=True)
    
    class Meta:
        model = SyncLog
        fields = [
            'id', 'sync', 'sync_name', 'status', 'status_display', 'records_processed',
            'records_successful', 'records_failed', 'error_message', 'details',
            'started_at', 'completed_at', 'duration'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']


class WebhookEndpointSerializer(serializers.ModelSerializer):
    """Serializer for webhook endpoints"""
    module_type_display = serializers.CharField(source='get_module_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = WebhookEndpoint
        fields = [
            'id', 'name', 'module_type', 'module_type_display', 'endpoint_path',
            'secret_key', 'status', 'status_display', 'is_enabled', 'handler_function',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WebhookLogSerializer(serializers.ModelSerializer):
    """Serializer for webhook logs"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    endpoint_name = serializers.CharField(source='endpoint.name', read_only=True)
    
    class Meta:
        model = WebhookLog
        fields = [
            'id', 'endpoint', 'endpoint_name', 'status', 'status_display', 'payload',
            'headers', 'ip_address', 'user_agent', 'response_data', 'error_message',
            'processing_time', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class IntegrationTestSerializer(serializers.ModelSerializer):
    """Serializer for integration tests"""
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    connection_name = serializers.CharField(source='connection.name', read_only=True)
    run_by_username = serializers.CharField(source='run_by.username', read_only=True)
    
    class Meta:
        model = IntegrationTest
        fields = [
            'id', 'name', 'connection', 'connection_name', 'test_type', 'test_type_display',
            'status', 'status_display', 'test_config', 'expected_result', 'actual_result',
            'error_message', 'run_by', 'run_by_username', 'started_at', 'completed_at', 'duration', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'started_at', 'completed_at']


class IntegrationSummarySerializer(serializers.Serializer):
    """Serializer for integration summary"""
    total_connections = serializers.IntegerField()
    active_connections = serializers.IntegerField()
    failed_connections = serializers.IntegerField()
    total_api_calls = serializers.IntegerField()
    successful_api_calls = serializers.IntegerField()
    failed_api_calls = serializers.IntegerField()
    total_syncs = serializers.IntegerField()
    active_syncs = serializers.IntegerField()
    total_webhooks = serializers.IntegerField()
    active_webhooks = serializers.IntegerField()
    last_updated = serializers.DateTimeField()


class ConnectionStatusSerializer(serializers.Serializer):
    """Serializer for connection status"""
    connection_name = serializers.CharField()
    module_type = serializers.CharField()
    status = serializers.CharField()
    last_checked = serializers.DateTimeField()
    response_time = serializers.FloatField()
    error_message = serializers.CharField()


class TestResultSerializer(serializers.Serializer):
    """Serializer for test results"""
    test_name = serializers.CharField()
    test_type = serializers.CharField()
    status = serializers.CharField()
    duration = serializers.FloatField()
    error_message = serializers.CharField()
    details = serializers.JSONField()
