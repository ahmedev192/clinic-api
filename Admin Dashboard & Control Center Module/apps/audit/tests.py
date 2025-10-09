"""
Tests for audit app
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import AuditLog, SystemLog, SecurityEvent, DataAccessLog


class AuditModelTests(TestCase):
    """Test audit models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_audit_log_creation(self):
        """Test audit log creation"""
        log = AuditLog.objects.create(
            user=self.user,
            action_type='create',
            resource_type='patient',
            description='Created new patient',
            result='success'
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action_type, 'create')
        self.assertEqual(log.resource_type, 'patient')
        self.assertEqual(log.result, 'success')
    
    def test_system_log_creation(self):
        """Test system log creation"""
        log = SystemLog.objects.create(
            level='INFO',
            component='dashboard',
            message='System started successfully',
            user=self.user
        )
        self.assertEqual(log.level, 'INFO')
        self.assertEqual(log.component, 'dashboard')
        self.assertEqual(log.message, 'System started successfully')
    
    def test_security_event_creation(self):
        """Test security event creation"""
        event = SecurityEvent.objects.create(
            event_type='failed_login',
            severity='medium',
            title='Failed Login Attempt',
            description='Multiple failed login attempts detected',
            user=self.user
        )
        self.assertEqual(event.event_type, 'failed_login')
        self.assertEqual(event.severity, 'medium')
        self.assertEqual(event.title, 'Failed Login Attempt')
    
    def test_data_access_log_creation(self):
        """Test data access log creation"""
        log = DataAccessLog.objects.create(
            user=self.user,
            access_type='view',
            resource_type='patient',
            ip_address='127.0.0.1'
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.access_type, 'view')
        self.assertEqual(log.resource_type, 'patient')


class AuditAPITests(APITestCase):
    """Test audit API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_audit_summary(self):
        """Test audit summary endpoint"""
        url = reverse('audit:audit_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_actions', response.data)
        self.assertIn('actions_today', response.data)
    
    def test_security_summary(self):
        """Test security summary endpoint"""
        url = reverse('audit:security_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_events', response.data)
        self.assertIn('critical_events', response.data)
    
    def test_compliance_summary(self):
        """Test compliance summary endpoint"""
        url = reverse('audit:compliance_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_reports', response.data)
        self.assertIn('pending_reports', response.data)
    
    def test_resolve_security_event(self):
        """Test resolve security event endpoint"""
        event = SecurityEvent.objects.create(
            event_type='failed_login',
            severity='medium',
            title='Test Security Event',
            description='Test security event'
        )
        
        url = reverse('audit:resolve_security_event', args=[event.id])
        data = {'resolution_notes': 'Resolved by admin'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        event.refresh_from_db()
        self.assertTrue(event.is_resolved)
        self.assertEqual(event.resolved_by, self.user)
    
    def test_log_event(self):
        """Test log event endpoint"""
        url = reverse('audit:log_event')
        data = {
            'action_type': 'create',
            'resource_type': 'patient',
            'description': 'Created new patient via API'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['action_type'], 'create')
    
    def test_audit_logs_list(self):
        """Test audit logs list"""
        AuditLog.objects.create(
            user=self.user,
            action_type='create',
            resource_type='patient',
            description='Test audit log'
        )
        
        url = reverse('audit:logs_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_security_events_list(self):
        """Test security events list"""
        SecurityEvent.objects.create(
            event_type='failed_login',
            severity='medium',
            title='Test Security Event',
            description='Test security event'
        )
        
        url = reverse('audit:security_events_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_data_access_logs_list(self):
        """Test data access logs list"""
        DataAccessLog.objects.create(
            user=self.user,
            access_type='view',
            resource_type='patient',
            ip_address='127.0.0.1'
        )
        
        url = reverse('audit:data_access_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
