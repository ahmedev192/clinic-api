from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import (
    AuditLog, SystemLog, SecurityEvent, DataAccessLog, 
    ComplianceReport, AuditConfiguration
)
from .serializers import (
    AuditLogSerializer, SystemLogSerializer, SecurityEventSerializer,
    DataAccessLogSerializer, ComplianceReportSerializer, AuditConfigurationSerializer,
    AuditSummarySerializer, SecuritySummarySerializer, ComplianceSummarySerializer
)
from .utils import (
    log_audit_event, log_system_event, log_security_event,
    log_data_access, generate_compliance_report, cleanup_old_logs
)

logger = logging.getLogger('admin_dashboard')


class AuditLogListCreateView(generics.ListCreateAPIView):
    """List and create audit logs"""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        action_type = self.request.query_params.get('action_type')
        resource_type = self.request.query_params.get('resource_type')
        result = self.request.query_params.get('result')
        days = int(self.request.query_params.get('days', 30))
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        if result:
            queryset = queryset.filter(result=result)
        
        # Filter by date range
        since = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(timestamp__gte=since)
        
        return queryset.order_by('-timestamp')


class SystemLogListCreateView(generics.ListCreateAPIView):
    """List and create system logs"""
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        level = self.request.query_params.get('level')
        component = self.request.query_params.get('component')
        user_id = self.request.query_params.get('user_id')
        days = int(self.request.query_params.get('days', 7))
        
        if level:
            queryset = queryset.filter(level=level)
        if component:
            queryset = queryset.filter(component=component)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by date range
        since = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(timestamp__gte=since)
        
        return queryset.order_by('-timestamp')


class SecurityEventListCreateView(generics.ListCreateAPIView):
    """List and create security events"""
    queryset = SecurityEvent.objects.all()
    serializer_class = SecurityEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        event_type = self.request.query_params.get('event_type')
        severity = self.request.query_params.get('severity')
        is_resolved = self.request.query_params.get('is_resolved')
        days = int(self.request.query_params.get('days', 30))
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if severity:
            queryset = queryset.filter(severity=severity)
        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved.lower() == 'true')
        
        # Filter by date range
        since = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(timestamp__gte=since)
        
        return queryset.order_by('-timestamp')


class DataAccessLogListCreateView(generics.ListCreateAPIView):
    """List and create data access logs"""
    queryset = DataAccessLog.objects.all()
    serializer_class = DataAccessLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        access_type = self.request.query_params.get('access_type')
        resource_type = self.request.query_params.get('resource_type')
        days = int(self.request.query_params.get('days', 30))
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if access_type:
            queryset = queryset.filter(access_type=access_type)
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        # Filter by date range
        since = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(timestamp__gte=since)
        
        return queryset.order_by('-timestamp')


class ComplianceReportListCreateView(generics.ListCreateAPIView):
    """List and create compliance reports"""
    queryset = ComplianceReport.objects.all()
    serializer_class = ComplianceReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        report_type = self.request.query_params.get('report_type')
        status_filter = self.request.query_params.get('status')
        
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-generated_at')


class AuditConfigurationListCreateView(generics.ListCreateAPIView):
    """List and create audit configurations"""
    queryset = AuditConfiguration.objects.all()
    serializer_class = AuditConfigurationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        component = self.request.query_params.get('component')
        is_enabled = self.request.query_params.get('is_enabled')
        
        if component:
            queryset = queryset.filter(component__icontains=component)
        if is_enabled is not None:
            queryset = queryset.filter(is_enabled=is_enabled.lower() == 'true')
        
        return queryset.order_by('component')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_summary(request):
    """Get audit summary for dashboard"""
    try:
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)
        
        # Get audit statistics
        total_actions = AuditLog.objects.count()
        actions_today = AuditLog.objects.filter(
            timestamp__date=timezone.now().date()
        ).count()
        actions_this_week = AuditLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=7)
        ).count()
        actions_this_month = AuditLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=30)
        ).count()
        failed_actions = AuditLog.objects.filter(result='failure').count()
        
        # Get security events
        security_events = SecurityEvent.objects.filter(timestamp__gte=since).count()
        
        # Get data access events
        data_access_events = DataAccessLog.objects.filter(timestamp__gte=since).count()
        
        summary_data = {
            'total_actions': total_actions,
            'actions_today': actions_today,
            'actions_this_week': actions_this_week,
            'actions_this_month': actions_this_month,
            'failed_actions': failed_actions,
            'security_events': security_events,
            'data_access_events': data_access_events,
            'last_updated': timezone.now()
        }
        
        serializer = AuditSummarySerializer(summary_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting audit summary: {str(e)}")
        return Response(
            {'error': f'Failed to get audit summary: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_summary(request):
    """Get security summary for dashboard"""
    try:
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)
        
        # Get security event statistics
        total_events = SecurityEvent.objects.count()
        critical_events = SecurityEvent.objects.filter(severity='critical').count()
        high_events = SecurityEvent.objects.filter(severity='high').count()
        medium_events = SecurityEvent.objects.filter(severity='medium').count()
        low_events = SecurityEvent.objects.filter(severity='low').count()
        unresolved_events = SecurityEvent.objects.filter(is_resolved=False).count()
        events_today = SecurityEvent.objects.filter(
            timestamp__date=timezone.now().date()
        ).count()
        
        summary_data = {
            'total_events': total_events,
            'critical_events': critical_events,
            'high_events': high_events,
            'medium_events': medium_events,
            'low_events': low_events,
            'unresolved_events': unresolved_events,
            'events_today': events_today,
            'last_updated': timezone.now()
        }
        
        serializer = SecuritySummarySerializer(summary_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting security summary: {str(e)}")
        return Response(
            {'error': f'Failed to get security summary: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compliance_summary(request):
    """Get compliance summary for dashboard"""
    try:
        # Get compliance report statistics
        total_reports = ComplianceReport.objects.count()
        pending_reports = ComplianceReport.objects.filter(status='pending').count()
        completed_reports = ComplianceReport.objects.filter(status='completed').count()
        failed_reports = ComplianceReport.objects.filter(status='failed').count()
        
        # Get reports by type
        reports_by_type = ComplianceReport.objects.values('report_type').annotate(
            count=Count('id')
        )
        reports_by_type = {item['report_type']: item['count'] for item in reports_by_type}
        
        summary_data = {
            'total_reports': total_reports,
            'pending_reports': pending_reports,
            'completed_reports': completed_reports,
            'failed_reports': failed_reports,
            'reports_by_type': reports_by_type,
            'last_updated': timezone.now()
        }
        
        serializer = ComplianceSummarySerializer(summary_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting compliance summary: {str(e)}")
        return Response(
            {'error': f'Failed to get compliance summary: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_security_event(request, event_id):
    """Resolve a security event"""
    try:
        event = SecurityEvent.objects.get(id=event_id)
        event.is_resolved = True
        event.resolved_at = timezone.now()
        event.resolved_by = request.user
        event.resolution_notes = request.data.get('resolution_notes', '')
        event.save()
        
        serializer = SecurityEventSerializer(event)
        return Response(serializer.data)
        
    except SecurityEvent.DoesNotExist:
        return Response(
            {'error': 'Security event not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error resolving security event: {str(e)}")
        return Response(
            {'error': f'Failed to resolve security event: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_compliance_report_api(request):
    """Generate a compliance report"""
    try:
        report_type = request.data.get('report_type')
        period_start = request.data.get('period_start')
        period_end = request.data.get('period_end')
        name = request.data.get('name', f"Compliance Report {timezone.now().strftime('%Y-%m-%d')}")
        
        if not all([report_type, period_start, period_end]):
            return Response(
                {'error': 'Report type, period start, and period end are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse dates
        try:
            period_start = datetime.fromisoformat(period_start.replace('Z', '+00:00'))
            period_end = datetime.fromisoformat(period_end.replace('Z', '+00:00'))
        except ValueError:
            return Response(
                {'error': 'Invalid date format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate report
        report = generate_compliance_report(
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            name=name,
            generated_by=request.user
        )
        
        if report:
            serializer = ComplianceReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to generate compliance report'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        logger.error(f"Error generating compliance report: {str(e)}")
        return Response(
            {'error': f'Failed to generate compliance report: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cleanup_logs(request):
    """Clean up old logs"""
    try:
        days = int(request.data.get('days', 365))
        results = cleanup_old_logs(days)
        return Response(results)
        
    except Exception as e:
        logger.error(f"Error cleaning up logs: {str(e)}")
        return Response(
            {'error': f'Failed to clean up logs: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_event(request):
    """Log an audit event via API"""
    try:
        action_type = request.data.get('action_type')
        resource_type = request.data.get('resource_type')
        description = request.data.get('description')
        resource_id = request.data.get('resource_id')
        old_values = request.data.get('old_values', {})
        new_values = request.data.get('new_values', {})
        metadata = request.data.get('metadata', {})
        
        if not all([action_type, resource_type, description]):
            return Response(
                {'error': 'Action type, resource type, and description are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log the event
        audit_log = log_audit_event(
            user=request.user,
            action_type=action_type,
            resource_type=resource_type,
            description=description,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            metadata=metadata,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            request_path=request.path,
            request_method=request.method
        )
        
        if audit_log:
            serializer = AuditLogSerializer(audit_log)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to log audit event'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        logger.error(f"Error logging audit event: {str(e)}")
        return Response(
            {'error': f'Failed to log audit event: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
