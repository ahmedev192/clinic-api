from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.

# Customize the admin site
admin.site.site_header = "Clinic Management System - Admin Dashboard"
admin.site.site_title = "Admin Dashboard"
admin.site.index_title = "Welcome to Admin Dashboard"

# Register models from all apps
from apps.dashboard.models import (
    DashboardConfiguration, SystemMetrics, QuickAction, DashboardWidget
)
from apps.monitoring.models import (
    SystemHealth, ModuleConnectivity, SystemAlert, PerformanceMetric, 
    ErrorLog, HealthCheck
)
from apps.analytics.models import (
    ReportTemplate, GeneratedReport, AnalyticsMetric, DashboardWidget as AnalyticsWidget,
    DataExport, ScheduledReport
)
from apps.notifications.models import (
    NotificationTemplate, Notification, NotificationRule, NotificationSubscription,
    AlertThreshold, NotificationQueue
)
from apps.audit.models import (
    AuditLog, SystemLog, SecurityEvent, DataAccessLog, 
    ComplianceReport, AuditConfiguration
)
from apps.integration.models import (
    ModuleConnection, APICall, DataSync, SyncLog, 
    WebhookEndpoint, WebhookLog, IntegrationTest
)


# Dashboard models
@admin.register(DashboardConfiguration)
class DashboardConfigurationAdmin(admin.ModelAdmin):
    list_display = ['role', 'enabled_widgets', 'refresh_interval', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['role']


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'value', 'unit', 'timestamp']
    list_filter = ['metric_type', 'timestamp']
    search_fields = ['metric_type']
    date_hierarchy = 'timestamp'


@admin.register(QuickAction)
class QuickActionAdmin(admin.ModelAdmin):
    list_display = ['name', 'action_type', 'is_active', 'order']
    list_filter = ['action_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'widget_type', 'is_active', 'order']
    list_filter = ['widget_type', 'is_active']
    search_fields = ['name', 'title']


# Monitoring models
@admin.register(SystemHealth)
class SystemHealthAdmin(admin.ModelAdmin):
    list_display = ['component', 'status', 'last_checked', 'response_time']
    list_filter = ['status', 'component', 'last_checked']
    search_fields = ['component', 'message']


@admin.register(ModuleConnectivity)
class ModuleConnectivityAdmin(admin.ModelAdmin):
    list_display = ['module_name', 'status', 'last_checked', 'response_time']
    list_filter = ['status', 'is_active']
    search_fields = ['module_name']


@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'priority', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'priority', 'is_resolved', 'created_at']
    search_fields = ['title', 'message']
    date_hierarchy = 'created_at'


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'value', 'component', 'timestamp']
    list_filter = ['metric_type', 'component', 'timestamp']
    search_fields = ['metric_type', 'component']
    date_hierarchy = 'timestamp'


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ['error_type', 'message', 'user', 'is_resolved', 'timestamp']
    list_filter = ['error_type', 'is_resolved', 'timestamp']
    search_fields = ['message', 'error_code']
    date_hierarchy = 'timestamp'


@admin.register(HealthCheck)
class HealthCheckAdmin(admin.ModelAdmin):
    list_display = ['name', 'check_type', 'is_active', 'last_status', 'last_run']
    list_filter = ['check_type', 'is_active', 'last_status']
    search_fields = ['name', 'endpoint']


# Analytics models
@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'is_active', 'created_by', 'created_at']
    list_filter = ['report_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'status', 'generated_by', 'generated_at']
    list_filter = ['status', 'generated_at']
    search_fields = ['name']
    date_hierarchy = 'generated_at'


@admin.register(AnalyticsMetric)
class AnalyticsMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'name', 'value', 'period_start', 'period_end']
    list_filter = ['metric_type', 'period_start']
    search_fields = ['name', 'metric_type']
    date_hierarchy = 'created_at'


@admin.register(AnalyticsWidget)
class AnalyticsWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'widget_type', 'is_active', 'created_by']
    list_filter = ['widget_type', 'is_active']
    search_fields = ['name', 'title']


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = ['name', 'export_type', 'status', 'requested_by', 'requested_at']
    list_filter = ['export_type', 'status', 'requested_at']
    search_fields = ['name']
    date_hierarchy = 'requested_at'


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'frequency', 'is_active', 'next_run']
    list_filter = ['frequency', 'is_active']
    search_fields = ['name']


# Notifications models
@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'notification_type', 'priority', 'is_active']
    list_filter = ['notification_type', 'priority', 'is_active']
    search_fields = ['name', 'title_template']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'priority', 'recipient', 'status', 'created_at']
    list_filter = ['notification_type', 'priority', 'status', 'created_at']
    search_fields = ['title', 'message']
    date_hierarchy = 'created_at'


@admin.register(NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'notification_type', 'is_active']
    list_filter = ['rule_type', 'notification_type', 'is_active']
    search_fields = ['name']


@admin.register(NotificationSubscription)
class NotificationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'channel', 'is_enabled']
    list_filter = ['notification_type', 'channel', 'is_enabled']
    search_fields = ['user__username']


@admin.register(AlertThreshold)
class AlertThresholdAdmin(admin.ModelAdmin):
    list_display = ['name', 'metric_type', 'threshold_value', 'is_active']
    list_filter = ['metric_type', 'is_active']
    search_fields = ['name']


@admin.register(NotificationQueue)
class NotificationQueueAdmin(admin.ModelAdmin):
    list_display = ['notification', 'status', 'scheduled_at', 'attempts']
    list_filter = ['status', 'scheduled_at']
    search_fields = ['notification__title']


# Audit models
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'resource_type', 'user', 'result', 'timestamp']
    list_filter = ['action_type', 'result', 'timestamp']
    search_fields = ['description', 'resource_type']
    date_hierarchy = 'timestamp'


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'component', 'message', 'user', 'timestamp']
    list_filter = ['level', 'component', 'timestamp']
    search_fields = ['message']
    date_hierarchy = 'timestamp'


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'severity', 'is_resolved', 'timestamp']
    list_filter = ['event_type', 'severity', 'is_resolved', 'timestamp']
    search_fields = ['title', 'description']
    date_hierarchy = 'timestamp'


@admin.register(DataAccessLog)
class DataAccessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'access_type', 'resource_type', 'timestamp']
    list_filter = ['access_type', 'resource_type', 'timestamp']
    search_fields = ['user__username', 'resource_type']
    date_hierarchy = 'timestamp'


@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'status', 'generated_by', 'generated_at']
    list_filter = ['report_type', 'status', 'generated_at']
    search_fields = ['name']
    date_hierarchy = 'generated_at'


@admin.register(AuditConfiguration)
class AuditConfigurationAdmin(admin.ModelAdmin):
    list_display = ['component', 'is_enabled', 'log_level', 'retention_days']
    list_filter = ['is_enabled', 'log_level']
    search_fields = ['component']


# Integration models
@admin.register(ModuleConnection)
class ModuleConnectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'module_type', 'status', 'is_enabled', 'last_checked']
    list_filter = ['module_type', 'status', 'is_enabled']
    search_fields = ['name', 'base_url']


@admin.register(APICall)
class APICallAdmin(admin.ModelAdmin):
    list_display = ['connection', 'endpoint', 'method', 'status', 'timestamp']
    list_filter = ['method', 'status', 'timestamp']
    search_fields = ['endpoint']
    date_hierarchy = 'timestamp'


@admin.register(DataSync)
class DataSyncAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_module', 'target_module', 'sync_type', 'status']
    list_filter = ['sync_type', 'status', 'is_enabled']
    search_fields = ['name']


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['sync', 'status', 'records_processed', 'started_at']
    list_filter = ['status', 'started_at']
    search_fields = ['sync__name']
    date_hierarchy = 'started_at'


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ['name', 'module_type', 'status', 'is_enabled']
    list_filter = ['module_type', 'status', 'is_enabled']
    search_fields = ['name', 'endpoint_path']


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ['endpoint', 'status', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['endpoint__name']
    date_hierarchy = 'timestamp'


@admin.register(IntegrationTest)
class IntegrationTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'connection', 'test_type', 'status', 'run_by']
    list_filter = ['test_type', 'status', 'created_at']
    search_fields = ['name']
    date_hierarchy = 'created_at'
