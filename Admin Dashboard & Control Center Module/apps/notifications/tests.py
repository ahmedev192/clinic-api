"""
Tests for notifications app
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import NotificationTemplate, Notification, AlertThreshold


class NotificationsModelTests(TestCase):
    """Test notifications models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_notification_template_creation(self):
        """Test notification template creation"""
        template = NotificationTemplate.objects.create(
            name='Test Template',
            notification_type='appointment',
            priority='medium',
            title_template='Test: {{title}}',
            message_template='Test message: {{message}}'
        )
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.notification_type, 'appointment')
        self.assertEqual(template.priority, 'medium')
    
    def test_notification_creation(self):
        """Test notification creation"""
        notification = Notification.objects.create(
            title='Test Notification',
            message='This is a test notification',
            notification_type='system',
            priority='high',
            recipient=self.user
        )
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.status, 'pending')
    
    def test_alert_threshold_creation(self):
        """Test alert threshold creation"""
        template = NotificationTemplate.objects.create(
            name='Test Template',
            notification_type='inventory'
        )
        
        threshold = AlertThreshold.objects.create(
            name='Low Stock Alert',
            metric_type='inventory_stock',
            threshold_value=10,
            comparison_operator='lt',
            notification_template=template
        )
        self.assertEqual(threshold.name, 'Low Stock Alert')
        self.assertEqual(threshold.metric_type, 'inventory_stock')
        self.assertEqual(threshold.threshold_value, 10)


class NotificationsAPITests(APITestCase):
    """Test notifications API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_notification_summary(self):
        """Test notification summary endpoint"""
        url = reverse('notifications:notification_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_notifications', response.data)
        self.assertIn('unread_notifications', response.data)
    
    def test_send_notification(self):
        """Test send notification endpoint"""
        url = reverse('notifications:send_notification')
        data = {
            'recipient_id': self.user.id,
            'title': 'Test Notification',
            'message': 'This is a test notification',
            'notification_type': 'system'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Notification')
    
    def test_mark_as_read(self):
        """Test mark notification as read"""
        notification = Notification.objects.create(
            title='Test Notification',
            message='This is a test notification',
            recipient=self.user
        )
        
        url = reverse('notifications:mark_as_read', args=[notification.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        notification.refresh_from_db()
        self.assertEqual(notification.status, 'read')
    
    def test_mark_all_as_read(self):
        """Test mark all notifications as read"""
        Notification.objects.create(
            title='Test Notification 1',
            message='This is a test notification',
            recipient=self.user
        )
        Notification.objects.create(
            title='Test Notification 2',
            message='This is another test notification',
            recipient=self.user
        )
        
        url = reverse('notifications:mark_all_as_read')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('notifications marked as read', response.data['message'])
    
    def test_notification_templates_list(self):
        """Test notification templates list"""
        NotificationTemplate.objects.create(
            name='Test Template',
            notification_type='appointment',
            title_template='Test: {{title}}'
        )
        
        url = reverse('notifications:templates_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_alert_thresholds_list(self):
        """Test alert thresholds list"""
        template = NotificationTemplate.objects.create(
            name='Test Template',
            notification_type='inventory'
        )
        
        AlertThreshold.objects.create(
            name='Test Threshold',
            metric_type='inventory_stock',
            threshold_value=10,
            notification_template=template
        )
        
        url = reverse('notifications:thresholds_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
