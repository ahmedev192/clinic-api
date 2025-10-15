from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    # System health
    path('health/', views.SystemHealthListCreateView.as_view(), name='health_list_create'),
    path('status/', views.system_status, name='system_status'),
    
    # Module connectivity
    path('connectivity/', views.ModuleConnectivityListCreateView.as_view(), name='connectivity_list_create'),
    
    # System alerts
    path('alerts/', views.SystemAlertListCreateView.as_view(), name='alerts_list_create'),
    path('alerts/<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    
    # Performance metrics
    path('performance/', views.PerformanceMetricListCreateView.as_view(), name='performance_list_create'),
    path('performance/summary/', views.performance_summary, name='performance_summary'),
    
    # Error logs
    path('errors/', views.ErrorLogListCreateView.as_view(), name='errors_list_create'),
    path('errors/<int:error_id>/resolve/', views.resolve_error, name='resolve_error'),
    
    # Health checks
    path('health-checks/', views.HealthCheckListCreateView.as_view(), name='health_checks_list_create'),
    path('health-checks/run/', views.run_health_check, name='run_health_check'),
]
