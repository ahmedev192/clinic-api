from django.urls import path
from . import views

app_name = 'integration'

urlpatterns = [
    # Module connections
    path('connections/', views.ModuleConnectionListCreateView.as_view(), name='connections_list_create'),
    path('connections/<int:connection_id>/test/', views.test_connection_api, name='test_connection'),
    
    # API calls
    path('api-calls/', views.APICallListCreateView.as_view(), name='api_calls_list_create'),
    path('api-calls/make/', views.make_api_call_api, name='make_api_call'),
    
    # Data syncs
    path('syncs/', views.DataSyncListCreateView.as_view(), name='syncs_list_create'),
    path('syncs/<int:sync_id>/run/', views.run_sync_api, name='run_sync'),
    
    # Sync logs
    path('sync-logs/', views.SyncLogListCreateView.as_view(), name='sync_logs_list_create'),
    
    # Webhook endpoints
    path('webhooks/', views.WebhookEndpointListCreateView.as_view(), name='webhooks_list_create'),
    path('webhooks/<str:endpoint_path>/', views.webhook_receiver, name='webhook_receiver'),
    
    # Webhook logs
    path('webhook-logs/', views.WebhookLogListCreateView.as_view(), name='webhook_logs_list_create'),
    
    # Integration tests
    path('tests/', views.IntegrationTestListCreateView.as_view(), name='tests_list_create'),
    path('tests/<int:test_id>/run/', views.run_integration_test_api, name='run_test'),
    path('tests/run-all/', views.run_all_tests, name='run_all_tests'),
    
    # Summaries
    path('summary/', views.integration_summary, name='integration_summary'),
    path('status/', views.connection_status, name='connection_status'),
]
