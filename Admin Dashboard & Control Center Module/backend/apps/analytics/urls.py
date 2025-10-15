from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Report templates
    path('templates/', views.ReportTemplateListCreateView.as_view(), name='templates_list_create'),
    
    # Generated reports
    path('reports/', views.GeneratedReportListCreateView.as_view(), name='reports_list_create'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    
    # Analytics metrics
    path('metrics/', views.AnalyticsMetricListCreateView.as_view(), name='metrics_list_create'),
    
    # Dashboard widgets
    path('widgets/', views.DashboardWidgetListCreateView.as_view(), name='widgets_list_create'),
    
    # Data exports
    path('exports/', views.DataExportListCreateView.as_view(), name='exports_list_create'),
    path('exports/request/', views.request_export, name='request_export'),
    
    # Scheduled reports
    path('scheduled/', views.ScheduledReportListCreateView.as_view(), name='scheduled_list_create'),
    path('scheduled/schedule/', views.schedule_report, name='schedule_report'),
    
    # Analytics data
    path('summary/', views.analytics_summary, name='analytics_summary'),
    path('chart-data/', views.chart_data, name='chart_data'),
    path('kpi-data/', views.kpi_data, name='kpi_data'),
]
