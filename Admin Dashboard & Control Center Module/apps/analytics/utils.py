"""
Utility functions for analytics app
"""
import requests
import logging
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .models import AnalyticsMetric

logger = logging.getLogger('admin_dashboard')


def generate_analytics_summary(period_start, period_end):
    """Generate analytics summary for a given period"""
    try:
        # This would integrate with other modules to get real data
        # For now, return mock data
        
        summary = {
            'period': f"{period_start.date()} to {period_end.date()}",
            'total_revenue': 125000.00,
            'total_patients': 1250,
            'total_appointments': 450,
            'total_consultations': 380,
            'average_appointment_duration': 45.5,
            'patient_satisfaction_score': 4.2,
            'staff_utilization_rate': 78.5,
            'generated_at': timezone.now()
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating analytics summary: {str(e)}")
        return {}


def generate_chart_data(chart_type, metric_type=None, days=30):
    """Generate chart data for visualization"""
    try:
        # Mock chart data - in production, this would fetch real data
        chart_data = {
            'chart_type': chart_type,
            'title': f"{metric_type or 'Analytics'} Chart",
            'data': {
                'labels': [],
                'datasets': []
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False
            },
            'generated_at': timezone.now()
        }
        
        # Generate sample data based on chart type
        if chart_type == 'line':
            chart_data['data'] = {
                'labels': [f"Day {i}" for i in range(1, days + 1)],
                'datasets': [{
                    'label': metric_type or 'Value',
                    'data': [100 + i * 5 + (i % 7) * 10 for i in range(days)],
                    'borderColor': 'rgb(75, 192, 192)',
                    'tension': 0.1
                }]
            }
        elif chart_type == 'bar':
            chart_data['data'] = {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'datasets': [{
                    'label': metric_type or 'Value',
                    'data': [65, 59, 80, 81, 56, 55],
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                }]
            }
        elif chart_type == 'pie':
            chart_data['data'] = {
                'labels': ['Category A', 'Category B', 'Category C', 'Category D'],
                'datasets': [{
                    'data': [30, 25, 20, 25],
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 205, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)'
                    ]
                }]
            }
        
        return chart_data
        
    except Exception as e:
        logger.error(f"Error generating chart data: {str(e)}")
        return {}


def generate_kpi_data():
    """Generate KPI data for dashboard"""
    try:
        kpis = [
            {
                'name': 'Total Revenue',
                'value': '$125,000',
                'unit': 'USD',
                'trend': 'up',
                'trend_value': 12.5,
                'color': 'success',
                'icon': 'dollar-sign'
            },
            {
                'name': 'Active Patients',
                'value': '1,250',
                'unit': 'patients',
                'trend': 'up',
                'trend_value': 8.3,
                'color': 'info',
                'icon': 'users'
            },
            {
                'name': 'Appointments Today',
                'value': '45',
                'unit': 'appointments',
                'trend': 'down',
                'trend_value': -2.1,
                'color': 'warning',
                'icon': 'calendar'
            },
            {
                'name': 'Staff Utilization',
                'value': '78.5%',
                'unit': 'percentage',
                'trend': 'up',
                'trend_value': 5.2,
                'color': 'primary',
                'icon': 'activity'
            },
            {
                'name': 'Patient Satisfaction',
                'value': '4.2',
                'unit': 'rating',
                'trend': 'up',
                'trend_value': 0.3,
                'color': 'success',
                'icon': 'star'
            },
            {
                'name': 'Inventory Alerts',
                'value': '3',
                'unit': 'alerts',
                'trend': 'down',
                'trend_value': -1,
                'color': 'danger',
                'icon': 'alert-triangle'
            }
        ]
        
        return kpis
        
    except Exception as e:
        logger.error(f"Error generating KPI data: {str(e)}")
        return []


def export_data(export_type, data_source, filters=None):
    """Export data in specified format"""
    try:
        # This would implement actual data export based on data_source
        # For now, return mock export info
        
        export_info = {
            'export_type': export_type,
            'data_source': data_source,
            'filters': filters or {},
            'file_path': f"/exports/export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{export_type}",
            'file_size': 1024,
            'record_count': 1000,
            'generated_at': timezone.now()
        }
        
        return export_info
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return None


def schedule_report(scheduled_report):
    """Schedule a report for execution"""
    try:
        # This would implement actual report scheduling
        # For now, just log the scheduling
        
        logger.info(f"Scheduled report '{scheduled_report.name}' for {scheduled_report.frequency}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error scheduling report: {str(e)}")
        return False


def calculate_metric_trend(metric_type, current_period, previous_period):
    """Calculate trend for a metric between two periods"""
    try:
        if not current_period or not previous_period:
            return 0
        
        if previous_period == 0:
            return 100 if current_period > 0 else 0
        
        trend = ((current_period - previous_period) / previous_period) * 100
        return round(trend, 2)
        
    except Exception as e:
        logger.error(f"Error calculating metric trend: {str(e)}")
        return 0


def get_module_analytics(module_name, metric_type, period_start, period_end):
    """Get analytics data from a specific module"""
    try:
        base_url = settings.MODULE_URLS.get(module_name.upper())
        if not base_url:
            logger.warning(f"No URL configured for module: {module_name}")
            return None
        
        # This would make actual API calls to the module
        # For now, return mock data
        mock_data = {
            'module': module_name,
            'metric_type': metric_type,
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'data': []
        }
        
        return mock_data
        
    except Exception as e:
        logger.error(f"Error getting module analytics: {str(e)}")
        return None


def aggregate_analytics_data(analytics_data_list):
    """Aggregate analytics data from multiple sources"""
    try:
        if not analytics_data_list:
            return {}
        
        aggregated = {
            'total_records': 0,
            'total_value': 0,
            'average_value': 0,
            'sources': len(analytics_data_list),
            'data': []
        }
        
        for data in analytics_data_list:
            if data and 'data' in data:
                aggregated['data'].extend(data['data'])
                aggregated['total_records'] += len(data['data'])
        
        if aggregated['total_records'] > 0:
            aggregated['average_value'] = aggregated['total_value'] / aggregated['total_records']
        
        return aggregated
        
    except Exception as e:
        logger.error(f"Error aggregating analytics data: {str(e)}")
        return {}


def create_analytics_metric(metric_type, name, value, unit=None, period_start=None, period_end=None, metadata=None):
    """Create an analytics metric record"""
    try:
        if not period_start:
            period_start = timezone.now() - timedelta(days=1)
        if not period_end:
            period_end = timezone.now()
        
        metric = AnalyticsMetric.objects.create(
            metric_type=metric_type,
            name=name,
            value=value,
            unit=unit,
            period_start=period_start,
            period_end=period_end,
            metadata=metadata or {}
        )
        
        logger.info(f"Analytics metric created: {name} = {value}")
        return metric
        
    except Exception as e:
        logger.error(f"Error creating analytics metric: {str(e)}")
        return None
