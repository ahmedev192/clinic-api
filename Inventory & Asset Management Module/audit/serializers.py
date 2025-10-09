"""
Audit serializers
"""
from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit log entries"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'action', 'action_display', 'object_repr', 'user', 'user_name',
            'content_type', 'content_type_name', 'object_id', 'changes', 'old_values',
            'new_values', 'reason', 'module', 'ip_address', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']
