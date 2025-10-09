"""
Tests for the analytics module.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json
from datetime import datetime, timedelta

from .models import ReportTemplate, ReportQuery, ReportResult, DataSource, ReportSchedule
from .serializers import (
    ReportTemplateSerializer, ReportQuerySerializer, FinancialReportSerializer,
    DemographicReportSerializer, DoctorPerformanceSerializer, AppointmentStatsSerializer,
    CustomReportSerializer, ExportRequestSerializer
)


class ReportTemplateModelTest(TestCase):
    """Test cases for ReportTemplate model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_create_template(self):
        """Test creating a report template."""
        template = ReportTemplate.objects.create(
            name='Test Template',
            name_ar='قالب اختبار',
            description='Test description',
            description_ar='وصف اختبار',
            report_type='financial',
            modules=['billing', 'payments'],
            filters={'include_outstanding': True},
            date_range={'default_period': 'last_month'},
            aggregation_fields={'revenue': 'sum'},
            group_by_fields=['department'],
            export_formats=['csv', 'excel'],
            include_charts=True,
            created_by=self.user
        )
        
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.name_ar, 'قالب اختبار')
        self.assertEqual(template.report_type, 'financial')
        self.assertTrue(template.is_active)
        self.assertEqual(template.created_by, self.user)
    
    def test_template_str(self):
        """Test string representation of template."""
        template = ReportTemplate.objects.create(
            name='Test Template',
            report_type='financial',
            created_by=self.user
        )
        self.assertEqual(str(template), 'Test Template')


class ReportQueryModelTest(TestCase):
    """Test cases for ReportQuery model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_create_query(self):
        """Test creating a report query."""
        query = ReportQuery.objects.create(
            name='Test Query',
            name_ar='استعلام اختبار',
            report_type='financial',
            filters={'department': 'Cardiology'},
            date_from=timezone.now() - timedelta(days=30),
            date_to=timezone.now(),
            group_by=['department'],
            aggregation={'revenue': 'sum'},
            created_by=self.user
        )
        
        self.assertEqual(query.name, 'Test Query')
        self.assertEqual(query.report_type, 'financial')
        self.assertEqual(query.status, 'pending')
        self.assertEqual(query.created_by, self.user)
    
    def test_query_str(self):
        """Test string representation of query."""
        query = ReportQuery.objects.create(
            name='Test Query',
            report_type='financial',
            date_from=timezone.now() - timedelta(days=30),
            date_to=timezone.now(),
            created_by=self.user
        )
        expected = f"Test Query - {query.get_status_display()}"
        self.assertEqual(str(query), expected)


class ReportResultModelTest(TestCase):
    """Test cases for ReportResult model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.query = ReportQuery.objects.create(
            name='Test Query',
            report_type='financial',
            date_from=timezone.now() - timedelta(days=30),
            date_to=timezone.now(),
            created_by=self.user
        )
        
    def test_create_result(self):
        """Test creating a report result."""
        result = ReportResult.objects.create(
            query=self.query,
            data={'summary': {'total_revenue': 100000}},
            summary={'total_revenue': 100000},
            metadata={'generated_at': timezone.now().isoformat()},
            cache_key='test_cache_key',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        self.assertEqual(result.query, self.query)
        self.assertEqual(result.data['summary']['total_revenue'], 100000)
        self.assertEqual(result.cache_key, 'test_cache_key')
    
    def test_result_str(self):
        """Test string representation of result."""
        result = ReportResult.objects.create(
            query=self.query,
            data={'summary': {'total_revenue': 100000}},
            summary={'total_revenue': 100000},
            cache_key='test_cache_key',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        expected = f"Result for {self.query.name}"
        self.assertEqual(str(result), expected)


class DataSourceModelTest(TestCase):
    """Test cases for DataSource model."""
    
    def test_create_data_source(self):
        """Test creating a data source."""
        source = DataSource.objects.create(
            name='Test Database',
            name_ar='قاعدة بيانات اختبار',
            source_type='database',
            connection_config={
                'host': 'localhost',
                'port': 5432,
                'database': 'test_db'
            }
        )
        
        self.assertEqual(source.name, 'Test Database')
        self.assertEqual(source.name_ar, 'قاعدة بيانات اختبار')
        self.assertEqual(source.source_type, 'database')
        self.assertTrue(source.is_active)
    
    def test_data_source_str(self):
        """Test string representation of data source."""
        source = DataSource.objects.create(
            name='Test Database',
            source_type='database',
            connection_config={}
        )
        self.assertEqual(str(source), 'Test Database')


class ReportScheduleModelTest(TestCase):
    """Test cases for ReportSchedule model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.template = ReportTemplate.objects.create(
            name='Test Template',
            report_type='financial',
            created_by=self.user
        )
        
    def test_create_schedule(self):
        """Test creating a report schedule."""
        schedule = ReportSchedule.objects.create(
            template=self.template,
            name='Daily Report',
            name_ar='تقرير يومي',
            frequency='daily',
            time='09:00:00',
            recipients=['admin@clinic.com', 'manager@clinic.com'],
            created_by=self.user
        )
        
        self.assertEqual(schedule.name, 'Daily Report')
        self.assertEqual(schedule.name_ar, 'تقرير يومي')
        self.assertEqual(schedule.frequency, 'daily')
        self.assertEqual(schedule.template, self.template)
        self.assertTrue(schedule.is_active)
    
    def test_schedule_str(self):
        """Test string representation of schedule."""
        schedule = ReportSchedule.objects.create(
            template=self.template,
            name='Daily Report',
            frequency='daily',
            time='09:00:00',
            created_by=self.user
        )
        expected = f"Daily Report - {schedule.get_frequency_display()}"
        self.assertEqual(str(schedule), expected)


class SerializerTest(TestCase):
    """Test cases for serializers."""
    
    def test_report_template_serializer(self):
        """Test ReportTemplateSerializer."""
        data = {
            'name': 'Test Template',
            'name_ar': 'قالب اختبار',
            'description': 'Test description',
            'description_ar': 'وصف اختبار',
            'report_type': 'financial',
            'modules': ['billing', 'payments'],
            'filters': {'include_outstanding': True},
            'date_range': {'default_period': 'last_month'},
            'aggregation_fields': {'revenue': 'sum'},
            'group_by_fields': ['department'],
            'export_formats': ['csv', 'excel'],
            'include_charts': True,
            'created_by_id': 1
        }
        
        serializer = ReportTemplateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_financial_report_serializer(self):
        """Test FinancialReportSerializer."""
        data = {
            'date_from': timezone.now() - timedelta(days=30),
            'date_to': timezone.now(),
            'department': 'Cardiology',
            'payment_type': 'Insurance'
        }
        
        serializer = FinancialReportSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_demographic_report_serializer(self):
        """Test DemographicReportSerializer."""
        data = {
            'date_from': timezone.now() - timedelta(days=30),
            'date_to': timezone.now(),
            'include_gender': True,
            'include_age_groups': True,
            'include_location': True,
            'include_visit_frequency': True
        }
        
        serializer = DemographicReportSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_doctor_performance_serializer(self):
        """Test DoctorPerformanceSerializer."""
        data = {
            'date_from': timezone.now() - timedelta(days=30),
            'date_to': timezone.now(),
            'doctor_ids': [1, 2, 3],
            'include_revenue': True,
            'include_consultation_time': True,
            'include_satisfaction': False
        }
        
        serializer = DoctorPerformanceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_appointment_stats_serializer(self):
        """Test AppointmentStatsSerializer."""
        data = {
            'date_from': timezone.now() - timedelta(days=7),
            'date_to': timezone.now(),
            'group_by': 'day',
            'include_no_shows': True,
            'include_cancellations': True,
            'include_peak_hours': True
        }
        
        serializer = AppointmentStatsSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_custom_report_serializer(self):
        """Test CustomReportSerializer."""
        data = {
            'name': 'Custom Report',
            'name_ar': 'تقرير مخصص',
            'modules': ['patients', 'appointments'],
            'filters': {'status': 'active'},
            'date_from': timezone.now() - timedelta(days=30),
            'date_to': timezone.now(),
            'group_by_fields': ['department'],
            'aggregation_fields': {'count': 'count'},
            'export_formats': ['csv', 'excel'],
            'save_template': False
        }
        
        serializer = CustomReportSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_export_request_serializer(self):
        """Test ExportRequestSerializer."""
        data = {
            'query_id': 1,
            'format': 'excel',
            'include_headers_ar': True,
            'include_headers_en': True
        }
        
        serializer = ExportRequestSerializer(data=data)
        # This will fail validation because query doesn't exist
        self.assertFalse(serializer.is_valid())


class APITest(APITestCase):
    """Test cases for API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_report_template_list(self):
        """Test listing report templates."""
        ReportTemplate.objects.create(
            name='Test Template',
            report_type='financial',
            created_by=self.user
        )
        
        url = reverse('reporttemplate-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_report_template_create(self):
        """Test creating a report template."""
        data = {
            'name': 'New Template',
            'name_ar': 'قالب جديد',
            'description': 'New template description',
            'description_ar': 'وصف قالب جديد',
            'report_type': 'financial',
            'modules': ['billing', 'payments'],
            'filters': {'include_outstanding': True},
            'date_range': {'default_period': 'last_month'},
            'aggregation_fields': {'revenue': 'sum'},
            'group_by_fields': ['department'],
            'export_formats': ['csv', 'excel'],
            'include_charts': True,
            'created_by_id': self.user.id
        }
        
        url = reverse('reporttemplate-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReportTemplate.objects.count(), 1)
    
    def test_financial_report_generate(self):
        """Test generating financial report."""
        data = {
            'date_from': timezone.now() - timedelta(days=30),
            'date_to': timezone.now(),
            'department': 'Cardiology',
            'payment_type': 'Insurance'
        }
        
        url = reverse('financial-generate')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
    
    def test_demographic_report_generate(self):
        """Test generating demographic report."""
        data = {
            'date_from': timezone.now() - timedelta(days=30),
            'date_to': timezone.now(),
            'include_gender': True,
            'include_age_groups': True,
            'include_location': True,
            'include_visit_frequency': True
        }
        
        url = reverse('demographic-generate')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
    
    def test_doctor_performance_generate(self):
        """Test generating doctor performance report."""
        data = {
            'date_from': timezone.now() - timedelta(days=30),
            'date_to': timezone.now(),
            'doctor_ids': [1, 2, 3],
            'include_revenue': True,
            'include_consultation_time': True,
            'include_satisfaction': False
        }
        
        url = reverse('doctor-performance-generate')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
    
    def test_appointment_stats_generate(self):
        """Test generating appointment statistics report."""
        data = {
            'date_from': timezone.now() - timedelta(days=7),
            'date_to': timezone.now(),
            'group_by': 'day',
            'include_no_shows': True,
            'include_cancellations': True,
            'include_peak_hours': True
        }
        
        url = reverse('appointment-stats-generate')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
    
    def test_custom_report_generate(self):
        """Test generating custom report."""
        data = {
            'name': 'Custom Report',
            'name_ar': 'تقرير مخصص',
            'modules': ['patients', 'appointments'],
            'filters': {'status': 'active'},
            'date_from': timezone.now() - timedelta(days=30),
            'date_to': timezone.now(),
            'group_by_fields': ['department'],
            'aggregation_fields': {'count': 'count'},
            'export_formats': ['csv', 'excel'],
            'save_template': False
        }
        
        url = reverse('custom-generate')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access endpoints."""
        self.client.logout()
        
        url = reverse('reporttemplate-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
