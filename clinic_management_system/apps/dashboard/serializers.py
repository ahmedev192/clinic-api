from rest_framework import serializers
from .models import DashboardConfiguration, SystemMetrics, QuickAction, DashboardWidget


class SystemMetricsSerializer(serializers.ModelSerializer):
    """Serializer for system metrics"""
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    
    class Meta:
        model = SystemMetrics
        fields = [
            'id', 'metric_type', 'metric_type_display', 'value', 'unit', 
            'timestamp', 'metadata'
        ]
        read_only_fields = ['id', 'timestamp']


class QuickActionSerializer(serializers.ModelSerializer):
    """Serializer for quick actions"""
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = QuickAction
        fields = [
            'id', 'name', 'action_type', 'action_type_display', 'url', 
            'icon', 'description', 'roles', 'is_active', 'order'
        ]
        read_only_fields = ['id', 'created_at']


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for dashboard widgets"""
    widget_type_display = serializers.CharField(source='get_widget_type_display', read_only=True)
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'name', 'widget_type', 'widget_type_display', 'title', 
            'description', 'data_source', 'configuration', 'roles', 
            'is_active', 'order', 'size', 'size_display'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for dashboard configuration"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = DashboardConfiguration
        fields = [
            'id', 'role', 'role_display', 'enabled_widgets', 
            'refresh_interval', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardOverviewSerializer(serializers.Serializer):
    """Serializer for dashboard overview data"""
    total_patients = serializers.IntegerField()
    active_patients = serializers.IntegerField()
    appointments_today = serializers.IntegerField()
    appointments_pending = serializers.IntegerField()
    consultations_today = serializers.IntegerField()
    doctors_active = serializers.IntegerField()
    staff_total = serializers.IntegerField()
    revenue_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    revenue_monthly = serializers.DecimalField(max_digits=15, decimal_places=2)
    invoices_pending = serializers.IntegerField()
    inventory_alerts = serializers.IntegerField()
    pharmacy_alerts = serializers.IntegerField()
    last_updated = serializers.DateTimeField()


class RoleBasedDataSerializer(serializers.Serializer):
    """Serializer for role-based data access"""
    user_role = serializers.CharField()
    accessible_modules = serializers.ListField(child=serializers.CharField())
    permissions = serializers.ListField(child=serializers.CharField())
    quick_actions = QuickActionSerializer(many=True)
    dashboard_widgets = DashboardWidgetSerializer(many=True)
