from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification templates
    path('templates/', views.NotificationTemplateListCreateView.as_view(), name='templates_list_create'),
    
    # Notifications
    path('', views.NotificationListCreateView.as_view(), name='notifications_list_create'),
    path('summary/', views.notification_summary, name='notification_summary'),
    path('stats/', views.notification_stats, name='notification_stats'),
    path('<int:notification_id>/mark-read/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('send/', views.send_notification_api, name='send_notification'),
    path('create-from-template/', views.create_from_template, name='create_from_template'),
    
    # Notification rules
    path('rules/', views.NotificationRuleListCreateView.as_view(), name='rules_list_create'),
    
    # Subscriptions
    path('subscriptions/', views.NotificationSubscriptionListCreateView.as_view(), name='subscriptions_list_create'),
    
    # Alert thresholds
    path('thresholds/', views.AlertThresholdListCreateView.as_view(), name='thresholds_list_create'),
    path('check-thresholds/', views.check_thresholds, name='check_thresholds'),
    
    # Queue
    path('queue/', views.NotificationQueueListCreateView.as_view(), name='queue_list_create'),
    path('process-queue/', views.process_queue, name='process_queue'),
]
