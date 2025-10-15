from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    # Audit logs
    path('logs/', views.AuditLogListCreateView.as_view(), name='logs_list_create'),
    path('logs/log-event/', views.log_event, name='log_event'),
    
    # System logs
    path('system-logs/', views.SystemLogListCreateView.as_view(), name='system_logs_list_create'),
    
    # Security events
    path('security-events/', views.SecurityEventListCreateView.as_view(), name='security_events_list_create'),
    path('security-events/<int:event_id>/resolve/', views.resolve_security_event, name='resolve_security_event'),
    
    # Data access logs
    path('data-access/', views.DataAccessLogListCreateView.as_view(), name='data_access_list_create'),
    
    # Compliance reports
    path('compliance-reports/', views.ComplianceReportListCreateView.as_view(), name='compliance_reports_list_create'),
    path('compliance-reports/generate/', views.generate_compliance_report_api, name='generate_compliance_report'),
    
    # Audit configuration
    path('configuration/', views.AuditConfigurationListCreateView.as_view(), name='configuration_list_create'),
    
    # Summaries
    path('summary/', views.audit_summary, name='audit_summary'),
    path('security-summary/', views.security_summary, name='security_summary'),
    path('compliance-summary/', views.compliance_summary, name='compliance_summary'),
    
    # Maintenance
    path('cleanup/', views.cleanup_logs, name='cleanup_logs'),
]
