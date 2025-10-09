from rest_framework import serializers
from .models import (
    NotificationTemplate, Notification, NotificationRule, 
    NotificationSubscription, NotificationLog, AlertThreshold, NotificationQueue
)


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'notification_type_display',
            'priority', 'priority_display', 'title_template', 'message_template',
            'variables', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'template', 'template_name', 'title', 'message',
            'notification_type', 'notification_type_display', 'priority', 'priority_display',
            'channel', 'channel_display', 'recipient', 'recipient_username',
            'status', 'status_display', 'data', 'sent_at', 'read_at', 'created_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'sent_at', 'read_at']


class NotificationRuleSerializer(serializers.ModelSerializer):
    """Serializer for notification rules"""
    rule_type_display = serializers.CharField(source='get_rule_type_display', read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = NotificationRule
        fields = [
            'id', 'name', 'rule_type', 'rule_type_display',
            'notification_type', 'notification_type_display', 'conditions',
            'template', 'template_name', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for notification subscriptions"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = NotificationSubscription
        fields = [
            'id', 'user', 'user_username', 'notification_type', 'notification_type_display',
            'channel', 'channel_display', 'is_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for notification logs"""
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    notification_title = serializers.CharField(source='notification.title', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'notification', 'notification_title', 'channel', 'channel_display',
            'status', 'status_display', 'error_message', 'response_data', 'attempted_at'
        ]
        read_only_fields = ['id', 'attempted_at']


class AlertThresholdSerializer(serializers.ModelSerializer):
    """Serializer for alert thresholds"""
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    comparison_operator_display = serializers.CharField(source='get_comparison_operator_display', read_only=True)
    template_name = serializers.CharField(source='notification_template.name', read_only=True)
    
    class Meta:
        model = AlertThreshold
        fields = [
            'id', 'name', 'metric_type', 'metric_type_display', 'threshold_value',
            'comparison_operator', 'comparison_operator_display', 'notification_template',
            'template_name', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationQueueSerializer(serializers.ModelSerializer):
    """Serializer for notification queue"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    notification_title = serializers.CharField(source='notification.title', read_only=True)
    
    class Meta:
        model = NotificationQueue
        fields = [
            'id', 'notification', 'notification_title', 'status', 'status_display',
            'scheduled_at', 'attempts', 'max_attempts', 'last_attempt_at',
            'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_attempt_at']


class NotificationSummarySerializer(serializers.Serializer):
    """Serializer for notification summary"""
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    pending_notifications = serializers.IntegerField()
    failed_notifications = serializers.IntegerField()
    notifications_by_type = serializers.JSONField()
    notifications_by_priority = serializers.JSONField()
    last_updated = serializers.DateTimeField()


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics"""
    period = serializers.CharField()
    total_sent = serializers.IntegerField()
    total_delivered = serializers.IntegerField()
    total_read = serializers.IntegerField()
    delivery_rate = serializers.FloatField()
    read_rate = serializers.FloatField()
    average_delivery_time = serializers.FloatField()
    generated_at = serializers.DateTimeField()
