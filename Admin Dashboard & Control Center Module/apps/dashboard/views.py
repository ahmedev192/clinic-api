from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import requests
from django.conf import settings

from .models import (
    DashboardConfiguration, SystemMetrics, QuickAction, DashboardWidget
)
from .serializers import (
    SystemMetricsSerializer, QuickActionSerializer, DashboardWidgetSerializer,
    DashboardConfigurationSerializer, DashboardOverviewSerializer, RoleBasedDataSerializer
)
from .utils import get_user_role, get_module_data, calculate_metrics


class SystemMetricsListCreateView(generics.ListCreateAPIView):
    """List and create system metrics"""
    queryset = SystemMetrics.objects.all()
    serializer_class = SystemMetricsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        metric_type = self.request.query_params.get('metric_type')
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        return queryset.order_by('-timestamp')


class QuickActionListCreateView(generics.ListCreateAPIView):
    """List and create quick actions"""
    queryset = QuickAction.objects.filter(is_active=True)
    serializer_class = QuickActionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_role = get_user_role(self.request.user)
        return self.queryset.filter(
            Q(roles__contains=[user_role]) | Q(roles__isnull=True)
        ).order_by('order')


class DashboardWidgetListCreateView(generics.ListCreateAPIView):
    """List and create dashboard widgets"""
    queryset = DashboardWidget.objects.filter(is_active=True)
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_role = get_user_role(self.request.user)
        return self.queryset.filter(
            Q(roles__contains=[user_role]) | Q(roles__isnull=True)
        ).order_by('order')


class DashboardConfigurationListCreateView(generics.ListCreateAPIView):
    """List and create dashboard configurations"""
    queryset = DashboardConfiguration.objects.all()
    serializer_class = DashboardConfigurationSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """Get dashboard overview statistics"""
    try:
        # Get current user role
        user_role = get_user_role(request.user)
        
        # Calculate metrics
        metrics = calculate_metrics(user_role)
        
        # Create overview data
        overview_data = {
            'total_patients': metrics.get('total_patients', 0),
            'active_patients': metrics.get('active_patients', 0),
            'appointments_today': metrics.get('appointments_today', 0),
            'appointments_pending': metrics.get('appointments_pending', 0),
            'consultations_today': metrics.get('consultations_today', 0),
            'doctors_active': metrics.get('doctors_active', 0),
            'staff_total': metrics.get('staff_total', 0),
            'revenue_total': metrics.get('revenue_total', 0),
            'revenue_monthly': metrics.get('revenue_monthly', 0),
            'invoices_pending': metrics.get('invoices_pending', 0),
            'inventory_alerts': metrics.get('inventory_alerts', 0),
            'pharmacy_alerts': metrics.get('pharmacy_alerts', 0),
            'last_updated': timezone.now()
        }
        
        serializer = DashboardOverviewSerializer(overview_data)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch dashboard overview: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def role_based_data(request):
    """Get role-based data for the current user"""
    try:
        user_role = get_user_role(request.user)
        
        # Get accessible modules based on role
        accessible_modules = get_accessible_modules(user_role)
        
        # Get permissions
        permissions = get_user_permissions(request.user, user_role)
        
        # Get quick actions for this role
        quick_actions = QuickAction.objects.filter(
            Q(roles__contains=[user_role]) | Q(roles__isnull=True),
            is_active=True
        ).order_by('order')
        
        # Get dashboard widgets for this role
        dashboard_widgets = DashboardWidget.objects.filter(
            Q(roles__contains=[user_role]) | Q(roles__isnull=True),
            is_active=True
        ).order_by('order')
        
        data = {
            'user_role': user_role,
            'accessible_modules': accessible_modules,
            'permissions': permissions,
            'quick_actions': quick_actions,
            'dashboard_widgets': dashboard_widgets
        }
        
        serializer = RoleBasedDataSerializer(data)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch role-based data: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def real_time_metrics(request):
    """Get real-time metrics for dashboard widgets"""
    try:
        user_role = get_user_role(request.user)
        metric_type = request.query_params.get('type')
        
        if metric_type:
            metrics = SystemMetrics.objects.filter(
                metric_type=metric_type
            ).order_by('-timestamp')[:10]
        else:
            metrics = SystemMetrics.objects.all().order_by('-timestamp')[:50]
        
        serializer = SystemMetricsSerializer(metrics, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch real-time metrics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_metrics(request):
    """Update system metrics (for background tasks)"""
    try:
        metric_data = request.data
        
        # Create or update metric
        metric, created = SystemMetrics.objects.update_or_create(
            metric_type=metric_data['metric_type'],
            timestamp__date=timezone.now().date(),
            defaults={
                'value': metric_data['value'],
                'unit': metric_data.get('unit', ''),
                'metadata': metric_data.get('metadata', {})
            }
        )
        
        serializer = SystemMetricsSerializer(metric)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to update metrics: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


def get_accessible_modules(user_role):
    """Get list of accessible modules based on user role"""
    role_modules = {
        'super_admin': [
            'auth', 'patient', 'doctor', 'appointment', 'consultation',
            'billing', 'pharmacy', 'laboratory', 'inventory', 'reporting'
        ],
        'admin': [
            'auth', 'patient', 'doctor', 'appointment', 'consultation',
            'billing', 'pharmacy', 'laboratory', 'inventory', 'reporting'
        ],
        'accountant': ['billing', 'reporting', 'patient'],
        'doctor': ['patient', 'appointment', 'consultation', 'laboratory'],
        'receptionist': ['patient', 'appointment', 'doctor'],
        'nurse': ['patient', 'appointment', 'consultation']
    }
    
    return role_modules.get(user_role, [])


def get_user_permissions(user, user_role):
    """Get user permissions based on role"""
    base_permissions = [
        'view_dashboard',
        'view_own_profile',
        'update_own_profile'
    ]
    
    role_permissions = {
        'super_admin': base_permissions + [
            'view_all_data', 'create_all_data', 'update_all_data', 'delete_all_data',
            'manage_users', 'manage_system', 'view_audit_logs', 'manage_integrations'
        ],
        'admin': base_permissions + [
            'view_all_data', 'create_all_data', 'update_all_data',
            'manage_users', 'view_audit_logs'
        ],
        'accountant': base_permissions + [
            'view_billing', 'create_billing', 'update_billing',
            'view_reports', 'view_patient_billing'
        ],
        'doctor': base_permissions + [
            'view_patients', 'create_consultations', 'update_consultations',
            'view_appointments', 'view_lab_results'
        ],
        'receptionist': base_permissions + [
            'view_patients', 'create_patients', 'update_patients',
            'view_appointments', 'create_appointments', 'update_appointments'
        ],
        'nurse': base_permissions + [
            'view_patients', 'view_appointments', 'view_consultations',
            'update_patient_vitals'
        ]
    }
    
    return role_permissions.get(user_role, base_permissions)
