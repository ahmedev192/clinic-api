"""
Tests for dashboard app
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import DashboardConfiguration, SystemMetrics, QuickAction, DashboardWidget


class DashboardModelTests(TestCase):
    """Test dashboard models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_dashboard_configuration_creation(self):
        """Test dashboard configuration creation"""
        config = DashboardConfiguration.objects.create(
            role='admin',
            enabled_widgets=['overview', 'monitoring'],
            refresh_interval=30
        )
        self.assertEqual(config.role, 'admin')
        self.assertEqual(len(config.enabled_widgets), 2)
        self.assertEqual(config.refresh_interval, 30)
    
    def test_system_metrics_creation(self):
        """Test system metrics creation"""
        metric = SystemMetrics.objects.create(
            metric_type='patients_total',
            value=100,
            unit='patients'
        )
        self.assertEqual(metric.metric_type, 'patients_total')
        self.assertEqual(metric.value, 100)
        self.assertEqual(metric.unit, 'patients')
    
    def test_quick_action_creation(self):
        """Test quick action creation"""
        action = QuickAction.objects.create(
            name='Test Action',
            action_type='create_patient',
            url='/test/',
            roles=['admin']
        )
        self.assertEqual(action.name, 'Test Action')
        self.assertEqual(action.action_type, 'create_patient')
        self.assertIn('admin', action.roles)
    
    def test_dashboard_widget_creation(self):
        """Test dashboard widget creation"""
        widget = DashboardWidget.objects.create(
            name='test_widget',
            widget_type='chart',
            title='Test Widget',
            data_source='/test/',
            roles=['admin']
        )
        self.assertEqual(widget.name, 'test_widget')
        self.assertEqual(widget.widget_type, 'chart')
        self.assertIn('admin', widget.roles)


class DashboardAPITests(APITestCase):
    """Test dashboard API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_dashboard_overview(self):
        """Test dashboard overview endpoint"""
        url = reverse('dashboard:dashboard_overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_patients', response.data)
        self.assertIn('appointments_today', response.data)
    
    def test_role_based_data(self):
        """Test role-based data endpoint"""
        url = reverse('dashboard:role_based_data')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_role', response.data)
        self.assertIn('accessible_modules', response.data)
    
    def test_system_metrics_list(self):
        """Test system metrics list endpoint"""
        SystemMetrics.objects.create(
            metric_type='patients_total',
            value=100,
            unit='patients'
        )
        
        url = reverse('dashboard:metrics_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_quick_actions_list(self):
        """Test quick actions list endpoint"""
        QuickAction.objects.create(
            name='Test Action',
            action_type='create_patient',
            url='/test/',
            roles=['admin']
        )
        
        url = reverse('dashboard:quick_actions_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_dashboard_widgets_list(self):
        """Test dashboard widgets list endpoint"""
        DashboardWidget.objects.create(
            name='test_widget',
            widget_type='chart',
            title='Test Widget',
            data_source='/test/',
            roles=['admin']
        )
        
        url = reverse('dashboard:widgets_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_update_metrics(self):
        """Test update metrics endpoint"""
        url = reverse('dashboard:update_metrics')
        data = {
            'metric_type': 'patients_total',
            'value': 150,
            'unit': 'patients'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['metric_type'], 'patients_total')
        self.assertEqual(response.data['value'], 150)
