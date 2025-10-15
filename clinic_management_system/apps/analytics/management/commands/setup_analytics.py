"""
Management command to set up analytics module with sample data.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from analytics.models import ReportTemplate, DataSource
import json


class Command(BaseCommand):
    help = 'Set up analytics module with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Setting up analytics module...')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@clinic.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        admin_user = User.objects.get(username='admin')
        
        # Create sample data sources
        data_sources = [
            {
                'name': 'Main Database',
                'name_ar': 'قاعدة البيانات الرئيسية',
                'source_type': 'database',
                'connection_config': {
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'clinic_db',
                    'username': 'postgres'
                }
            },
            {
                'name': 'Insurance API',
                'name_ar': 'واجهة برمجة التأمين',
                'source_type': 'api',
                'connection_config': {
                    'base_url': 'https://api.insurance.com',
                    'api_key': 'your_api_key_here',
                    'timeout': 30
                }
            }
        ]
        
        for source_data in data_sources:
            source, created = DataSource.objects.get_or_create(
                name=source_data['name'],
                defaults=source_data
            )
            if created:
                self.stdout.write(f'Created data source: {source.name}')
        
        # Create sample report templates
        templates = [
            {
                'name': 'Monthly Financial Report',
                'name_ar': 'التقرير المالي الشهري',
                'description': 'Comprehensive monthly financial analysis',
                'description_ar': 'تحليل مالي شامل شهري',
                'report_type': 'financial',
                'modules': ['billing', 'payments', 'expenses'],
                'filters': {
                    'include_outstanding': True,
                    'include_breakdown': True
                },
                'date_range': {
                    'default_period': 'last_month',
                    'custom_range': True
                },
                'aggregation_fields': {
                    'revenue': 'sum',
                    'expenses': 'sum',
                    'profit': 'calculated'
                },
                'group_by_fields': ['department', 'payment_type'],
                'export_formats': ['csv', 'excel', 'pdf'],
                'include_charts': True
            },
            {
                'name': 'Patient Demographics',
                'name_ar': 'ديموغرافيا المرضى',
                'description': 'Patient demographic analysis and statistics',
                'description_ar': 'تحليل وإحصائيات ديموغرافيا المرضى',
                'report_type': 'demographic',
                'modules': ['patients'],
                'filters': {
                    'include_gender': True,
                    'include_age_groups': True,
                    'include_location': True
                },
                'date_range': {
                    'default_period': 'last_quarter',
                    'custom_range': True
                },
                'aggregation_fields': {
                    'count': 'count',
                    'age_avg': 'avg'
                },
                'group_by_fields': ['gender', 'age_group', 'city'],
                'export_formats': ['csv', 'excel'],
                'include_charts': True
            },
            {
                'name': 'Doctor Performance Analysis',
                'name_ar': 'تحليل أداء الأطباء',
                'description': 'Doctor performance metrics and analysis',
                'description_ar': 'مقاييس وتحليل أداء الأطباء',
                'report_type': 'doctor_performance',
                'modules': ['doctors', 'consultations', 'billing'],
                'filters': {
                    'include_revenue': True,
                    'include_consultation_time': True,
                    'include_satisfaction': False
                },
                'date_range': {
                    'default_period': 'last_month',
                    'custom_range': True
                },
                'aggregation_fields': {
                    'consultations': 'count',
                    'revenue': 'sum',
                    'avg_time': 'avg'
                },
                'group_by_fields': ['doctor', 'specialization'],
                'export_formats': ['csv', 'excel', 'pdf'],
                'include_charts': True
            },
            {
                'name': 'Appointment Statistics',
                'name_ar': 'إحصائيات المواعيد',
                'description': 'Appointment volume and efficiency analysis',
                'description_ar': 'تحليل حجم وكفاءة المواعيد',
                'report_type': 'appointment_stats',
                'modules': ['appointments'],
                'filters': {
                    'include_no_shows': True,
                    'include_cancellations': True,
                    'include_peak_hours': True
                },
                'date_range': {
                    'default_period': 'last_week',
                    'custom_range': True
                },
                'aggregation_fields': {
                    'total': 'count',
                    'completed': 'count',
                    'no_show_rate': 'calculated'
                },
                'group_by_fields': ['date', 'hour', 'department'],
                'export_formats': ['csv', 'excel'],
                'include_charts': True
            }
        ]
        
        for template_data in templates:
            template, created = ReportTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    **template_data,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f'Created template: {template.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Analytics module setup completed successfully!')
        )

