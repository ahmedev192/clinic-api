"""
Management command to set up the admin dashboard with initial data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from apps.dashboard.models import DashboardConfiguration, QuickAction, DashboardWidget
from apps.notifications.models import NotificationTemplate, AlertThreshold
from apps.integration.models import ModuleConnection
from apps.audit.models import AuditConfiguration


class Command(BaseCommand):
    help = 'Set up the admin dashboard with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Setting up admin dashboard...')
        
        # Create user groups
        self.create_groups()
        
        # Create dashboard configurations
        self.create_dashboard_configurations()
        
        # Create quick actions
        self.create_quick_actions()
        
        # Create dashboard widgets
        self.create_dashboard_widgets()
        
        # Create notification templates
        self.create_notification_templates()
        
        # Create alert thresholds
        self.create_alert_thresholds()
        
        # Create module connections
        self.create_module_connections()
        
        # Create audit configurations
        self.create_audit_configurations()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up admin dashboard!')
        )

    def create_groups(self):
        """Create user groups"""
        groups = [
            'Super Admin',
            'Admin',
            'Accountant',
            'Doctor',
            'Receptionist',
            'Nurse'
        ]
        
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f'Created group: {group_name}')

    def create_dashboard_configurations(self):
        """Create dashboard configurations for different roles"""
        configurations = [
            {
                'role': 'super_admin',
                'enabled_widgets': ['overview', 'monitoring', 'analytics', 'notifications', 'audit'],
                'refresh_interval': 30
            },
            {
                'role': 'admin',
                'enabled_widgets': ['overview', 'monitoring', 'analytics', 'notifications'],
                'refresh_interval': 30
            },
            {
                'role': 'accountant',
                'enabled_widgets': ['overview', 'billing', 'reports'],
                'refresh_interval': 60
            },
            {
                'role': 'doctor',
                'enabled_widgets': ['overview', 'patients', 'appointments', 'consultations'],
                'refresh_interval': 60
            },
            {
                'role': 'receptionist',
                'enabled_widgets': ['overview', 'patients', 'appointments', 'doctors'],
                'refresh_interval': 60
            },
            {
                'role': 'nurse',
                'enabled_widgets': ['overview', 'patients', 'appointments'],
                'refresh_interval': 60
            }
        ]
        
        for config in configurations:
            dashboard_config, created = DashboardConfiguration.objects.get_or_create(
                role=config['role'],
                defaults={
                    'enabled_widgets': config['enabled_widgets'],
                    'refresh_interval': config['refresh_interval']
                }
            )
            if created:
                self.stdout.write(f'Created dashboard config for: {config["role"]}')

    def create_quick_actions(self):
        """Create quick actions for different roles"""
        actions = [
            {
                'name': 'Create Patient',
                'action_type': 'create_patient',
                'url': '/api/patients/create/',
                'icon': 'user-plus',
                'description': 'Add a new patient to the system',
                'roles': ['super_admin', 'admin', 'receptionist'],
                'order': 1
            },
            {
                'name': 'Schedule Appointment',
                'action_type': 'schedule_appointment',
                'url': '/api/appointments/create/',
                'icon': 'calendar-plus',
                'description': 'Schedule a new appointment',
                'roles': ['super_admin', 'admin', 'receptionist', 'doctor'],
                'order': 2
            },
            {
                'name': 'View Reports',
                'action_type': 'view_reports',
                'url': '/api/analytics/reports/',
                'icon': 'bar-chart',
                'description': 'View system reports and analytics',
                'roles': ['super_admin', 'admin', 'accountant'],
                'order': 3
            },
            {
                'name': 'Manage Inventory',
                'action_type': 'manage_inventory',
                'url': '/api/inventory/',
                'icon': 'package',
                'description': 'Manage inventory and stock',
                'roles': ['super_admin', 'admin'],
                'order': 4
            },
            {
                'name': 'Process Payment',
                'action_type': 'process_payment',
                'url': '/api/billing/payments/',
                'icon': 'credit-card',
                'description': 'Process patient payments',
                'roles': ['super_admin', 'admin', 'accountant', 'receptionist'],
                'order': 5
            },
            {
                'name': 'View Analytics',
                'action_type': 'view_analytics',
                'url': '/api/analytics/summary/',
                'icon': 'trending-up',
                'description': 'View system analytics',
                'roles': ['super_admin', 'admin', 'accountant'],
                'order': 6
            }
        ]
        
        for action_data in actions:
            action, created = QuickAction.objects.get_or_create(
                name=action_data['name'],
                defaults=action_data
            )
            if created:
                self.stdout.write(f'Created quick action: {action_data["name"]}')

    def create_dashboard_widgets(self):
        """Create dashboard widgets"""
        widgets = [
            {
                'name': 'overview_stats',
                'widget_type': 'stat_card',
                'title': 'Overview Statistics',
                'description': 'Key statistics for the clinic',
                'data_source': '/api/dashboard/overview/',
                'configuration': {'size': 'large'},
                'roles': ['super_admin', 'admin', 'accountant', 'doctor', 'receptionist', 'nurse'],
                'order': 1,
                'size': 'large'
            },
            {
                'name': 'recent_appointments',
                'widget_type': 'table',
                'title': 'Recent Appointments',
                'description': 'Latest appointments scheduled',
                'data_source': '/api/appointments/recent/',
                'configuration': {'rows': 10},
                'roles': ['super_admin', 'admin', 'doctor', 'receptionist'],
                'order': 2,
                'size': 'medium'
            },
            {
                'name': 'system_health',
                'widget_type': 'chart',
                'title': 'System Health',
                'description': 'System health monitoring',
                'data_source': '/api/monitoring/status/',
                'configuration': {'chart_type': 'gauge'},
                'roles': ['super_admin', 'admin'],
                'order': 3,
                'size': 'small'
            },
            {
                'name': 'revenue_chart',
                'widget_type': 'chart',
                'title': 'Revenue Trend',
                'description': 'Revenue trend over time',
                'data_source': '/api/analytics/revenue-chart/',
                'configuration': {'chart_type': 'line'},
                'roles': ['super_admin', 'admin', 'accountant'],
                'order': 4,
                'size': 'medium'
            },
            {
                'name': 'notifications',
                'widget_type': 'list',
                'title': 'Recent Notifications',
                'description': 'Latest system notifications',
                'data_source': '/api/notifications/recent/',
                'configuration': {'limit': 5},
                'roles': ['super_admin', 'admin', 'doctor', 'receptionist', 'nurse'],
                'order': 5,
                'size': 'small'
            }
        ]
        
        for widget_data in widgets:
            widget, created = DashboardWidget.objects.get_or_create(
                name=widget_data['name'],
                defaults=widget_data
            )
            if created:
                self.stdout.write(f'Created dashboard widget: {widget_data["name"]}')

    def create_notification_templates(self):
        """Create notification templates"""
        templates = [
            {
                'name': 'Appointment Reminder',
                'notification_type': 'appointment',
                'priority': 'medium',
                'title_template': 'Appointment Reminder - {{patient_name}}',
                'message_template': 'You have an appointment scheduled for {{appointment_date}} at {{appointment_time}} with Dr. {{doctor_name}}.',
                'variables': ['patient_name', 'appointment_date', 'appointment_time', 'doctor_name']
            },
            {
                'name': 'Inventory Low Stock',
                'notification_type': 'inventory',
                'priority': 'high',
                'title_template': 'Low Stock Alert - {{item_name}}',
                'message_template': 'Inventory item {{item_name}} is running low. Current stock: {{current_stock}}, Minimum required: {{minimum_stock}}.',
                'variables': ['item_name', 'current_stock', 'minimum_stock']
            },
            {
                'name': 'Payment Due',
                'notification_type': 'billing',
                'priority': 'medium',
                'title_template': 'Payment Due - {{patient_name}}',
                'message_template': 'Payment of ${{amount}} is due for patient {{patient_name}}. Due date: {{due_date}}.',
                'variables': ['patient_name', 'amount', 'due_date']
            },
            {
                'name': 'System Error',
                'notification_type': 'system',
                'priority': 'critical',
                'title_template': 'System Error - {{component}}',
                'message_template': 'A system error occurred in {{component}}: {{error_message}}',
                'variables': ['component', 'error_message']
            }
        ]
        
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'Created notification template: {template_data["name"]}')

    def create_alert_thresholds(self):
        """Create alert thresholds"""
        thresholds = [
            {
                'name': 'Low Inventory Stock',
                'metric_type': 'inventory_stock',
                'threshold_value': 10,
                'comparison_operator': 'lt',
                'notification_template': NotificationTemplate.objects.get(name='Inventory Low Stock')
            },
            {
                'name': 'High Error Rate',
                'metric_type': 'error_rate',
                'threshold_value': 5.0,
                'comparison_operator': 'gt',
                'notification_template': NotificationTemplate.objects.get(name='System Error')
            },
            {
                'name': 'High Response Time',
                'metric_type': 'response_time',
                'threshold_value': 5.0,
                'comparison_operator': 'gt',
                'notification_template': NotificationTemplate.objects.get(name='System Error')
            }
        ]
        
        for threshold_data in thresholds:
            threshold, created = AlertThreshold.objects.get_or_create(
                name=threshold_data['name'],
                defaults=threshold_data
            )
            if created:
                self.stdout.write(f'Created alert threshold: {threshold_data["name"]}')

    def create_module_connections(self):
        """Create module connections"""
        connections = [
            {
                'name': 'Auth Module',
                'module_type': 'auth',
                'base_url': 'http://localhost:8001/api/',
                'status': 'inactive'
            },
            {
                'name': 'Patient Module',
                'module_type': 'patient',
                'base_url': 'http://localhost:8002/api/',
                'status': 'inactive'
            },
            {
                'name': 'Doctor Module',
                'module_type': 'doctor',
                'base_url': 'http://localhost:8003/api/',
                'status': 'inactive'
            },
            {
                'name': 'Appointment Module',
                'module_type': 'appointment',
                'base_url': 'http://localhost:8004/api/',
                'status': 'inactive'
            },
            {
                'name': 'Consultation Module',
                'module_type': 'consultation',
                'base_url': 'http://localhost:8005/api/',
                'status': 'inactive'
            },
            {
                'name': 'Billing Module',
                'module_type': 'billing',
                'base_url': 'http://localhost:8006/api/',
                'status': 'inactive'
            },
            {
                'name': 'Pharmacy Module',
                'module_type': 'pharmacy',
                'base_url': 'http://localhost:8007/api/',
                'status': 'inactive'
            },
            {
                'name': 'Laboratory Module',
                'module_type': 'laboratory',
                'base_url': 'http://localhost:8008/api/',
                'status': 'inactive'
            },
            {
                'name': 'Inventory Module',
                'module_type': 'inventory',
                'base_url': 'http://localhost:8009/api/',
                'status': 'inactive'
            },
            {
                'name': 'Reporting Module',
                'module_type': 'reporting',
                'base_url': 'http://localhost:8010/api/',
                'status': 'inactive'
            }
        ]
        
        for connection_data in connections:
            connection, created = ModuleConnection.objects.get_or_create(
                name=connection_data['name'],
                defaults=connection_data
            )
            if created:
                self.stdout.write(f'Created module connection: {connection_data["name"]}')

    def create_audit_configurations(self):
        """Create audit configurations"""
        configurations = [
            {
                'component': 'dashboard',
                'is_enabled': True,
                'log_level': 'INFO',
                'retention_days': 365,
                'log_actions': ['create', 'update', 'delete', 'read'],
                'exclude_users': []
            },
            {
                'component': 'monitoring',
                'is_enabled': True,
                'log_level': 'WARNING',
                'retention_days': 180,
                'log_actions': ['create', 'update', 'delete'],
                'exclude_users': []
            },
            {
                'component': 'analytics',
                'is_enabled': True,
                'log_level': 'INFO',
                'retention_days': 365,
                'log_actions': ['create', 'update', 'delete', 'read'],
                'exclude_users': []
            },
            {
                'component': 'notifications',
                'is_enabled': True,
                'log_level': 'INFO',
                'retention_days': 90,
                'log_actions': ['create', 'update', 'delete'],
                'exclude_users': []
            },
            {
                'component': 'audit',
                'is_enabled': True,
                'log_level': 'DEBUG',
                'retention_days': 730,
                'log_actions': ['create', 'update', 'delete', 'read'],
                'exclude_users': []
            },
            {
                'component': 'integration',
                'is_enabled': True,
                'log_level': 'INFO',
                'retention_days': 180,
                'log_actions': ['create', 'update', 'delete'],
                'exclude_users': []
            }
        ]
        
        for config_data in configurations:
            config, created = AuditConfiguration.objects.get_or_create(
                component=config_data['component'],
                defaults=config_data
            )
            if created:
                self.stdout.write(f'Created audit configuration: {config_data["component"]}')
