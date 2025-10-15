"""
Tests for analytics app
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import ReportTemplate, GeneratedReport, AnalyticsMetric, DataExport


class AnalyticsModelTests(TestCase):
    """Test analytics models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_report_template_creation(self):
        """Test report template creation"""
        template = ReportTemplate.objects.create(
            name='Test Report',
            report_type='financial',
            description='Test financial report',
            query_config={'filters': []},
            created_by=self.user
        )
        self.assertEqual(template.name, 'Test Report')
        self.assertEqual(template.report_type, 'financial')
        self.assertEqual(template.created_by, self.user)
    
    def test_generated_report_creation(self):
        """Test generated report creation"""
        template = ReportTemplate.objects.create(
            name='Test Template',
            report_type='financial'
        )
        
        report = GeneratedReport.objects.create(
            template=template,
            name='Generated Test Report',
            generated_by=self.user
        )
        self.assertEqual(report.template, template)
        self.assertEqual(report.name, 'Generated Test Report')
        self.assertEqual(report.generated_by, self.user)
    
    def test_analytics_metric_creation(self):
        """Test analytics metric creation"""
        metric = AnalyticsMetric.objects.create(
            metric_type='revenue',
            name='Monthly Revenue',
            value=10000.50,
            unit='USD'
        )
        self.assertEqual(metric.metric_type, 'revenue')
        self.assertEqual(metric.name, 'Monthly Revenue')
        self.assertEqual(metric.value, 10000.50)
    
    def test_data_export_creation(self):
        """Test data export creation"""
        export = DataExport.objects.create(
            name='Test Export',
            export_type='csv',
            data_source='patients',
            requested_by=self.user
        )
        self.assertEqual(export.name, 'Test Export')
        self.assertEqual(export.export_type, 'csv')
        self.assertEqual(export.requested_by, self.user)


class AnalyticsAPITests(APITestCase):
    """Test analytics API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_analytics_summary(self):
        """Test analytics summary endpoint"""
        url = reverse('analytics:analytics_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue', response.data)
        self.assertIn('total_patients', response.data)
    
    def test_chart_data(self):
        """Test chart data endpoint"""
        url = reverse('analytics:chart_data')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('chart_type', response.data)
        self.assertIn('data', response.data)
    
    def test_kpi_data(self):
        """Test KPI data endpoint"""
        url = reverse('analytics:kpi_data')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_generate_report(self):
        """Test generate report endpoint"""
        template = ReportTemplate.objects.create(
            name='Test Template',
            report_type='financial'
        )
        
        url = reverse('analytics:generate_report')
        data = {
            'template_id': template.id,
            'parameters': {}
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['template'], template.id)
    
    def test_request_export(self):
        """Test request export endpoint"""
        url = reverse('analytics:request_export')
        data = {
            'export_type': 'csv',
            'data_source': 'patients',
            'name': 'Test Export'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['export_type'], 'csv')
