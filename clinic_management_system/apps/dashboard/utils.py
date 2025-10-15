"""
Utility functions for dashboard app
"""
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('admin_dashboard')


def get_user_role(user):
    """Get user role from user groups or custom logic"""
    if user.is_superuser:
        return 'super_admin'
    
    # Check if user has specific groups
    if user.groups.filter(name='Admin').exists():
        return 'admin'
    elif user.groups.filter(name='Accountant').exists():
        return 'accountant'
    elif user.groups.filter(name='Doctor').exists():
        return 'doctor'
    elif user.groups.filter(name='Receptionist').exists():
        return 'receptionist'
    elif user.groups.filter(name='Nurse').exists():
        return 'nurse'
    
    # Default role
    return 'receptionist'


def get_module_data(module_name, endpoint, params=None):
    """
    Fetch data from external modules
    This is a placeholder for future integration
    """
    try:
        base_url = settings.MODULE_URLS.get(module_name.upper())
        if not base_url:
            logger.warning(f"No URL configured for module: {module_name}")
            return None
        
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from {module_name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching data from {module_name}: {str(e)}")
        return None


def calculate_metrics(user_role):
    """
    Calculate dashboard metrics
    This function will integrate with other modules in the future
    """
    metrics = {}
    
    try:
        # For now, return mock data
        # In production, this will fetch real data from other modules
        
        # Patient metrics
        patient_data = get_module_data('patient', 'statistics/')
        if patient_data:
            metrics['total_patients'] = patient_data.get('total_patients', 0)
            metrics['active_patients'] = patient_data.get('active_patients', 0)
        else:
            # Mock data for development
            metrics['total_patients'] = 1250
            metrics['active_patients'] = 890
        
        # Appointment metrics
        appointment_data = get_module_data('appointment', 'statistics/today/')
        if appointment_data:
            metrics['appointments_today'] = appointment_data.get('today_count', 0)
            metrics['appointments_pending'] = appointment_data.get('pending_count', 0)
        else:
            metrics['appointments_today'] = 45
            metrics['appointments_pending'] = 12
        
        # Consultation metrics
        consultation_data = get_module_data('consultation', 'statistics/today/')
        if consultation_data:
            metrics['consultations_today'] = consultation_data.get('today_count', 0)
        else:
            metrics['consultations_today'] = 38
        
        # Staff metrics
        doctor_data = get_module_data('doctor', 'statistics/')
        if doctor_data:
            metrics['doctors_active'] = doctor_data.get('active_doctors', 0)
            metrics['staff_total'] = doctor_data.get('total_staff', 0)
        else:
            metrics['doctors_active'] = 15
            metrics['staff_total'] = 45
        
        # Billing metrics
        billing_data = get_module_data('billing', 'statistics/')
        if billing_data:
            metrics['revenue_total'] = billing_data.get('total_revenue', 0)
            metrics['revenue_monthly'] = billing_data.get('monthly_revenue', 0)
            metrics['invoices_pending'] = billing_data.get('pending_invoices', 0)
        else:
            metrics['revenue_total'] = 125000.00
            metrics['revenue_monthly'] = 15000.00
            metrics['invoices_pending'] = 8
        
        # Inventory metrics
        inventory_data = get_module_data('inventory', 'alerts/')
        if inventory_data:
            metrics['inventory_alerts'] = inventory_data.get('low_stock_count', 0)
        else:
            metrics['inventory_alerts'] = 3
        
        # Pharmacy metrics
        pharmacy_data = get_module_data('pharmacy', 'alerts/')
        if pharmacy_data:
            metrics['pharmacy_alerts'] = pharmacy_data.get('low_stock_count', 0)
        else:
            metrics['pharmacy_alerts'] = 2
        
        # Filter metrics based on user role
        if user_role in ['accountant', 'super_admin', 'admin']:
            # Full access to all metrics
            pass
        elif user_role == 'doctor':
            # Limited access for doctors
            metrics = {k: v for k, v in metrics.items() 
                      if k in ['total_patients', 'active_patients', 'appointments_today', 
                              'consultations_today', 'doctors_active']}
        elif user_role == 'receptionist':
            # Limited access for receptionists
            metrics = {k: v for k, v in metrics.items() 
                      if k in ['total_patients', 'active_patients', 'appointments_today', 
                              'appointments_pending', 'doctors_active']}
        elif user_role == 'nurse':
            # Limited access for nurses
            metrics = {k: v for k, v in metrics.items() 
                      if k in ['total_patients', 'active_patients', 'appointments_today', 
                              'consultations_today']}
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        return {}


def get_dashboard_widgets(user_role):
    """Get dashboard widgets based on user role"""
    from .models import DashboardWidget
    
    return DashboardWidget.objects.filter(
        Q(roles__contains=[user_role]) | Q(roles__isnull=True),
        is_active=True
    ).order_by('order')


def get_quick_actions(user_role):
    """Get quick actions based on user role"""
    from .models import QuickAction
    
    return QuickAction.objects.filter(
        Q(roles__contains=[user_role]) | Q(roles__isnull=True),
        is_active=True
    ).order_by('order')


def check_module_connectivity():
    """Check connectivity to all modules"""
    connectivity_status = {}
    
    for module_name, base_url in settings.MODULE_URLS.items():
        try:
            response = requests.get(f"{base_url}health/", timeout=5)
            connectivity_status[module_name] = {
                'status': 'connected' if response.status_code == 200 else 'error',
                'response_time': response.elapsed.total_seconds(),
                'last_checked': timezone.now()
            }
        except requests.exceptions.RequestException:
            connectivity_status[module_name] = {
                'status': 'disconnected',
                'response_time': None,
                'last_checked': timezone.now()
            }
    
    return connectivity_status


def generate_dashboard_summary(user_role, date_range=None):
    """Generate a comprehensive dashboard summary"""
    if not date_range:
        date_range = {
            'start': timezone.now().date() - timedelta(days=30),
            'end': timezone.now().date()
        }
    
    summary = {
        'date_range': date_range,
        'user_role': user_role,
        'metrics': calculate_metrics(user_role),
        'connectivity': check_module_connectivity(),
        'generated_at': timezone.now()
    }
    
    return summary
