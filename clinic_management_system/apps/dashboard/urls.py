from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard overview
    path('overview/', views.dashboard_overview, name='dashboard_overview'),
    path('role-based-data/', views.role_based_data, name='role_based_data'),
    path('real-time-metrics/', views.real_time_metrics, name='real_time_metrics'),
    path('update-metrics/', views.update_metrics, name='update_metrics'),
    
    # System metrics
    path('metrics/', views.SystemMetricsListCreateView.as_view(), name='metrics_list_create'),
    
    # Quick actions
    path('quick-actions/', views.QuickActionListCreateView.as_view(), name='quick_actions_list_create'),
    
    # Dashboard widgets
    path('widgets/', views.DashboardWidgetListCreateView.as_view(), name='widgets_list_create'),
    
    # Dashboard configuration
    path('configuration/', views.DashboardConfigurationListCreateView.as_view(), name='configuration_list_create'),
]
