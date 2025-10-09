"""
Tests for monitoring app
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import SystemHealth, ModuleConnectivity, SystemAlert, PerformanceMetric


class MonitoringModelTests(TestCase):
    """Test monitoring models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_system_health_creation(self):
        """Test system health creation"""
        health = SystemHealth.objects.create(
            component='database',
            status='healthy',
            message='Database is running normally'
        )
        self.assertEqual(health.component, 'database')
        self.assertEqual(health.status, 'healthy')
        self.assertEqual(health.message, 'Database is running normally')
    
    def test_module_connectivity_creation(self):
        """Test module connectivity creation"""
        connectivity = ModuleConnectivity.objects.create(
            module_name='test_module',
            base_url='http://localhost:8000/api/',
            status='connected'
        )
        self.assertEqual(connectivity.module_name, 'test_module')
        self.assertEqual(connectivity.status, 'connected')
    
    def test_system_alert_creation(self):
        """Test system alert creation"""
        alert = SystemAlert.objects.create(
            alert_type='warning',
            priority='high',
            title='Test Alert',
            message='This is a test alert',
            component='test_component'
        )
        self.assertEqual(alert.alert_type, 'warning')
        self.assertEqual(alert.priority, 'high')
        self.assertEqual(alert.title, 'Test Alert')
    
    def test_performance_metric_creation(self):
        """Test performance metric creation"""
        metric = PerformanceMetric.objects.create(
            metric_type='response_time',
            value=1.5,
            unit='seconds',
            component='api'
        )
        self.assertEqual(metric.metric_type, 'response_time')
        self.assertEqual(metric.value, 1.5)
        self.assertEqual(metric.component, 'api')


class MonitoringAPITests(APITestCase):
    """Test monitoring API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_system_status(self):
        """Test system status endpoint"""
        url = reverse('monitoring:system_status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('overall_status', response.data)
        self.assertIn('healthy_components', response.data)
    
    def test_system_health_list(self):
        """Test system health list endpoint"""
        SystemHealth.objects.create(
            component='database',
            status='healthy',
            message='Database is running normally'
        )
        
        url = reverse('monitoring:health_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_module_connectivity_list(self):
        """Test module connectivity list endpoint"""
        ModuleConnectivity.objects.create(
            module_name='test_module',
            base_url='http://localhost:8000/api/',
            status='connected'
        )
        
        url = reverse('monitoring:connectivity_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_system_alerts_list(self):
        """Test system alerts list endpoint"""
        SystemAlert.objects.create(
            alert_type='warning',
            priority='high',
            title='Test Alert',
            message='This is a test alert'
        )
        
        url = reverse('monitoring:alerts_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_performance_metrics_list(self):
        """Test performance metrics list endpoint"""
        PerformanceMetric.objects.create(
            metric_type='response_time',
            value=1.5,
            unit='seconds',
            component='api'
        )
        
        url = reverse('monitoring:performance_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_resolve_alert(self):
        """Test resolve alert endpoint"""
        alert = SystemAlert.objects.create(
            alert_type='warning',
            priority='high',
            title='Test Alert',
            message='This is a test alert'
        )
        
        url = reverse('monitoring:resolve_alert', args=[alert.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        alert.refresh_from_db()
        self.assertTrue(alert.is_resolved)
        self.assertEqual(alert.resolved_by, self.user)
    
    def test_performance_summary(self):
        """Test performance summary endpoint"""
        PerformanceMetric.objects.create(
            metric_type='response_time',
            value=1.5,
            unit='seconds',
            component='api'
        )
        
        url = reverse('monitoring:performance_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response_times', response.data)
        self.assertIn('error_rates', response.data)
