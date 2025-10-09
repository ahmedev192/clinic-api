"""
Tests for integration app
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import ModuleConnection, APICall, DataSync, IntegrationTest


class IntegrationModelTests(TestCase):
    """Test integration models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_module_connection_creation(self):
        """Test module connection creation"""
        connection = ModuleConnection.objects.create(
            name='Test Module',
            module_type='patient',
            base_url='http://localhost:8000/api/',
            status='active'
        )
        self.assertEqual(connection.name, 'Test Module')
        self.assertEqual(connection.module_type, 'patient')
        self.assertEqual(connection.status, 'active')
    
    def test_api_call_creation(self):
        """Test API call creation"""
        connection = ModuleConnection.objects.create(
            name='Test Module',
            module_type='patient',
            base_url='http://localhost:8000/api/'
        )
        
        api_call = APICall.objects.create(
            connection=connection,
            endpoint='patients/',
            method='GET',
            status='success',
            initiated_by=self.user
        )
        self.assertEqual(api_call.connection, connection)
        self.assertEqual(api_call.endpoint, 'patients/')
        self.assertEqual(api_call.method, 'GET')
        self.assertEqual(api_call.status, 'success')
    
    def test_data_sync_creation(self):
        """Test data sync creation"""
        source_connection = ModuleConnection.objects.create(
            name='Source Module',
            module_type='patient',
            base_url='http://localhost:8001/api/'
        )
        
        target_connection = ModuleConnection.objects.create(
            name='Target Module',
            module_type='analytics',
            base_url='http://localhost:8002/api/'
        )
        
        sync = DataSync.objects.create(
            name='Test Sync',
            source_module=source_connection,
            target_module=target_connection,
            sync_type='one_way',
            source_endpoint='patients/',
            target_endpoint='analytics/patients/'
        )
        self.assertEqual(sync.name, 'Test Sync')
        self.assertEqual(sync.source_module, source_connection)
        self.assertEqual(sync.target_module, target_connection)
    
    def test_integration_test_creation(self):
        """Test integration test creation"""
        connection = ModuleConnection.objects.create(
            name='Test Module',
            module_type='patient',
            base_url='http://localhost:8000/api/'
        )
        
        test = IntegrationTest.objects.create(
            name='Test Connection',
            connection=connection,
            test_type='connectivity',
            run_by=self.user
        )
        self.assertEqual(test.name, 'Test Connection')
        self.assertEqual(test.connection, connection)
        self.assertEqual(test.test_type, 'connectivity')


class IntegrationAPITests(APITestCase):
    """Test integration API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_integration_summary(self):
        """Test integration summary endpoint"""
        url = reverse('integration:integration_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_connections', response.data)
        self.assertIn('active_connections', response.data)
    
    def test_connection_status(self):
        """Test connection status endpoint"""
        ModuleConnection.objects.create(
            name='Test Module',
            module_type='patient',
            base_url='http://localhost:8000/api/',
            is_enabled=True
        )
        
        url = reverse('integration:connection_status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_test_connection(self):
        """Test test connection endpoint"""
        connection = ModuleConnection.objects.create(
            name='Test Module',
            module_type='patient',
            base_url='http://localhost:8000/api/'
        )
        
        url = reverse('integration:test_connection', args=[connection.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
    
    def test_make_api_call(self):
        """Test make API call endpoint"""
        connection = ModuleConnection.objects.create(
            name='Test Module',
            module_type='patient',
            base_url='http://localhost:8000/api/'
        )
        
        url = reverse('integration:make_api_call')
        data = {
            'connection_id': connection.id,
            'endpoint': 'patients/',
            'method': 'GET'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['connection'], connection.id)
    
    def test_run_sync(self):
        """Test run sync endpoint"""
        source_connection = ModuleConnection.objects.create(
            name='Source Module',
            module_type='patient',
            base_url='http://localhost:8001/api/'
        )
        
        target_connection = ModuleConnection.objects.create(
            name='Target Module',
            module_type='analytics',
            base_url='http://localhost:8002/api/'
        )
        
        sync = DataSync.objects.create(
            name='Test Sync',
            source_module=source_connection,
            target_module=target_connection,
            sync_type='one_way',
            source_endpoint='patients/',
            target_endpoint='analytics/patients/'
        )
        
        url = reverse('integration:run_sync', args=[sync.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['sync'], sync.id)
    
    def test_run_integration_test(self):
        """Test run integration test endpoint"""
        connection = ModuleConnection.objects.create(
            name='Test Module',
            module_type='patient',
            base_url='http://localhost:8000/api/'
        )
        
        test = IntegrationTest.objects.create(
            name='Test Connection',
            connection=connection,
            test_type='connectivity'
        )
        
        url = reverse('integration:run_test', args=[test.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], test.id)
    
    def test_run_all_tests(self):
        """Test run all tests endpoint"""
        connection = ModuleConnection.objects.create(
            name='Test Module',
            module_type='patient',
            base_url='http://localhost:8000/api/'
        )
        
        IntegrationTest.objects.create(
            name='Test 1',
            connection=connection,
            test_type='connectivity'
        )
        
        IntegrationTest.objects.create(
            name='Test 2',
            connection=connection,
            test_type='authentication'
        )
        
        url = reverse('integration:run_all_tests')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_module_connections_list(self):
        """Test module connections list"""
        ModuleConnection.objects.create(
            name='Test Module',
            module_type='patient',
            base_url='http://localhost:8000/api/'
        )
        
        url = reverse('integration:connections_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_api_calls_list(self):
        """Test API calls list"""
        connection = ModuleConnection.objects.create(
            name='Test Module',
            module_type='patient',
            base_url='http://localhost:8000/api/'
        )
        
        APICall.objects.create(
            connection=connection,
            endpoint='patients/',
            method='GET',
            status='success'
        )
        
        url = reverse('integration:api_calls_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
