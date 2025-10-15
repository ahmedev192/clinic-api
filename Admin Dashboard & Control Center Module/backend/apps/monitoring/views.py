from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import requests
import psutil
import logging
from django.conf import settings

from .models import (
    SystemHealth, ModuleConnectivity, SystemAlert, 
    PerformanceMetric, ErrorLog, HealthCheck
)
from .serializers import (
    SystemHealthSerializer, ModuleConnectivitySerializer, SystemAlertSerializer,
    PerformanceMetricSerializer, ErrorLogSerializer, HealthCheckSerializer,
    SystemStatusSerializer, HealthCheckResultSerializer
)
from .utils import check_system_health, check_module_connectivity, run_health_checks

logger = logging.getLogger('admin_dashboard')


class SystemHealthListCreateView(generics.ListCreateAPIView):
    """List and create system health records"""
    queryset = SystemHealth.objects.all()
    serializer_class = SystemHealthSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        component = self.request.query_params.get('component')
        status_filter = self.request.query_params.get('status')
        
        if component:
            queryset = queryset.filter(component__icontains=component)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-last_checked')


class ModuleConnectivityListCreateView(generics.ListCreateAPIView):
    """List and create module connectivity records"""
    queryset = ModuleConnectivity.objects.all()
    serializer_class = ModuleConnectivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        module_name = self.request.query_params.get('module_name')
        status_filter = self.request.query_params.get('status')
        
        if module_name:
            queryset = queryset.filter(module_name__icontains=module_name)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('module_name')


class SystemAlertListCreateView(generics.ListCreateAPIView):
    """List and create system alerts"""
    queryset = SystemAlert.objects.all()
    serializer_class = SystemAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        alert_type = self.request.query_params.get('alert_type')
        priority = self.request.query_params.get('priority')
        is_resolved = self.request.query_params.get('is_resolved')
        
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        if priority:
            queryset = queryset.filter(priority=priority)
        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved.lower() == 'true')
        
        return queryset.order_by('-created_at')


class PerformanceMetricListCreateView(generics.ListCreateAPIView):
    """List and create performance metrics"""
    queryset = PerformanceMetric.objects.all()
    serializer_class = PerformanceMetricSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        metric_type = self.request.query_params.get('metric_type')
        component = self.request.query_params.get('component')
        hours = self.request.query_params.get('hours', 24)
        
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        if component:
            queryset = queryset.filter(component__icontains=component)
        
        # Filter by time range
        since = timezone.now() - timedelta(hours=int(hours))
        queryset = queryset.filter(timestamp__gte=since)
        
        return queryset.order_by('-timestamp')


class ErrorLogListCreateView(generics.ListCreateAPIView):
    """List and create error logs"""
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        error_type = self.request.query_params.get('error_type')
        is_resolved = self.request.query_params.get('is_resolved')
        hours = self.request.query_params.get('hours', 24)
        
        if error_type:
            queryset = queryset.filter(error_type=error_type)
        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved.lower() == 'true')
        
        # Filter by time range
        since = timezone.now() - timedelta(hours=int(hours))
        queryset = queryset.filter(timestamp__gte=since)
        
        return queryset.order_by('-timestamp')


class HealthCheckListCreateView(generics.ListCreateAPIView):
    """List and create health checks"""
    queryset = HealthCheck.objects.all()
    serializer_class = HealthCheckSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_status(request):
    """Get overall system status"""
    try:
        # Get system health summary
        health_components = SystemHealth.objects.values('status').annotate(count=Count('id'))
        health_summary = {item['status']: item['count'] for item in health_components}
        
        # Get module connectivity summary
        connectivity_components = ModuleConnectivity.objects.values('status').annotate(count=Count('id'))
        connectivity_summary = {item['status']: item['count'] for item in connectivity_components}
        
        # Get active alerts count
        active_alerts = SystemAlert.objects.filter(is_resolved=False).count()
        
        # Determine overall status
        if health_summary.get('critical', 0) > 0:
            overall_status = 'critical'
        elif health_summary.get('warning', 0) > 0:
            overall_status = 'warning'
        elif connectivity_summary.get('disconnected', 0) > 0:
            overall_status = 'warning'
        else:
            overall_status = 'healthy'
        
        status_data = {
            'overall_status': overall_status,
            'healthy_components': health_summary.get('healthy', 0),
            'warning_components': health_summary.get('warning', 0),
            'critical_components': health_summary.get('critical', 0),
            'connected_modules': connectivity_summary.get('connected', 0),
            'disconnected_modules': connectivity_summary.get('disconnected', 0),
            'active_alerts': active_alerts,
            'last_updated': timezone.now()
        }
        
        serializer = SystemStatusSerializer(status_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return Response(
            {'error': f'Failed to get system status: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_health_check(request):
    """Run health checks manually"""
    try:
        check_name = request.data.get('check_name')
        if check_name:
            # Run specific health check
            try:
                health_check = HealthCheck.objects.get(name=check_name)
                result = run_health_checks([health_check])
                return Response(result[0] if result else {'error': 'Health check failed'})
            except HealthCheck.DoesNotExist:
                return Response(
                    {'error': 'Health check not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Run all active health checks
            health_checks = HealthCheck.objects.filter(is_active=True)
            results = run_health_checks(health_checks)
            return Response(results)
        
    except Exception as e:
        logger.error(f"Error running health check: {str(e)}")
        return Response(
            {'error': f'Failed to run health check: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def performance_summary(request):
    """Get performance summary"""
    try:
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        # Get average response times by component
        response_times = PerformanceMetric.objects.filter(
            metric_type='response_time',
            timestamp__gte=since
        ).values('component').annotate(
            avg_response_time=Avg('value')
        ).order_by('component')
        
        # Get error rates
        error_rates = PerformanceMetric.objects.filter(
            metric_type='error_rate',
            timestamp__gte=since
        ).values('component').annotate(
            avg_error_rate=Avg('value')
        ).order_by('component')
        
        # Get system resource usage
        system_metrics = PerformanceMetric.objects.filter(
            metric_type__in=['cpu_usage', 'memory_usage', 'disk_usage'],
            timestamp__gte=since
        ).values('metric_type').annotate(
            avg_value=Avg('value')
        ).order_by('metric_type')
        
        summary = {
            'time_range_hours': hours,
            'response_times': list(response_times),
            'error_rates': list(error_rates),
            'system_metrics': list(system_metrics),
            'generated_at': timezone.now()
        }
        
        return Response(summary)
        
    except Exception as e:
        logger.error(f"Error getting performance summary: {str(e)}")
        return Response(
            {'error': f'Failed to get performance summary: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_alert(request, alert_id):
    """Resolve a system alert"""
    try:
        alert = SystemAlert.objects.get(id=alert_id)
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save()
        
        serializer = SystemAlertSerializer(alert)
        return Response(serializer.data)
        
    except SystemAlert.DoesNotExist:
        return Response(
            {'error': 'Alert not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        return Response(
            {'error': f'Failed to resolve alert: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_error(request, error_id):
    """Resolve an error log"""
    try:
        error = ErrorLog.objects.get(id=error_id)
        error.is_resolved = True
        error.resolved_at = timezone.now()
        error.save()
        
        serializer = ErrorLogSerializer(error)
        return Response(serializer.data)
        
    except ErrorLog.DoesNotExist:
        return Response(
            {'error': 'Error log not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error resolving error log: {str(e)}")
        return Response(
            {'error': f'Failed to resolve error log: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
