from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import (
    ReportTemplate, GeneratedReport, AnalyticsMetric, 
    DashboardWidget, DataExport, ScheduledReport
)
from .serializers import (
    ReportTemplateSerializer, GeneratedReportSerializer, AnalyticsMetricSerializer,
    DashboardWidgetSerializer, DataExportSerializer, ScheduledReportSerializer,
    AnalyticsSummarySerializer, ChartDataSerializer, KPISerializer
)
from .utils import (
    generate_analytics_summary, generate_chart_data, 
    generate_kpi_data, export_data, schedule_report
)

logger = logging.getLogger('admin_dashboard')


class ReportTemplateListCreateView(generics.ListCreateAPIView):
    """List and create report templates"""
    queryset = ReportTemplate.objects.filter(is_active=True)
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        report_type = self.request.query_params.get('report_type')
        
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        return queryset.order_by('name')


class GeneratedReportListCreateView(generics.ListCreateAPIView):
    """List and create generated reports"""
    queryset = GeneratedReport.objects.all()
    serializer_class = GeneratedReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        template_id = self.request.query_params.get('template_id')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        
        return queryset.order_by('-generated_at')


class AnalyticsMetricListCreateView(generics.ListCreateAPIView):
    """List and create analytics metrics"""
    queryset = AnalyticsMetric.objects.all()
    serializer_class = AnalyticsMetricSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        metric_type = self.request.query_params.get('metric_type')
        days = int(self.request.query_params.get('days', 30))
        
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        # Filter by date range
        since = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(created_at__gte=since)
        
        return queryset.order_by('-created_at')


class DashboardWidgetListCreateView(generics.ListCreateAPIView):
    """List and create dashboard widgets"""
    queryset = DashboardWidget.objects.filter(is_active=True)
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        widget_type = self.request.query_params.get('widget_type')
        
        if widget_type:
            queryset = queryset.filter(widget_type=widget_type)
        
        return queryset.order_by('name')


class DataExportListCreateView(generics.ListCreateAPIView):
    """List and create data exports"""
    queryset = DataExport.objects.all()
    serializer_class = DataExportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        export_type = self.request.query_params.get('export_type')
        status_filter = self.request.query_params.get('status')
        
        if export_type:
            queryset = queryset.filter(export_type=export_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-requested_at')


class ScheduledReportListCreateView(generics.ListCreateAPIView):
    """List and create scheduled reports"""
    queryset = ScheduledReport.objects.all()
    serializer_class = ScheduledReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_summary(request):
    """Get analytics summary for dashboard"""
    try:
        days = int(request.query_params.get('days', 30))
        period_start = timezone.now() - timedelta(days=days)
        period_end = timezone.now()
        
        summary_data = generate_analytics_summary(period_start, period_end)
        serializer = AnalyticsSummarySerializer(summary_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error generating analytics summary: {str(e)}")
        return Response(
            {'error': f'Failed to generate analytics summary: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chart_data(request):
    """Get chart data for specific metrics"""
    try:
        chart_type = request.query_params.get('type', 'line')
        metric_type = request.query_params.get('metric_type')
        days = int(request.query_params.get('days', 30))
        
        chart_data = generate_chart_data(chart_type, metric_type, days)
        serializer = ChartDataSerializer(chart_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error generating chart data: {str(e)}")
        return Response(
            {'error': f'Failed to generate chart data: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kpi_data(request):
    """Get KPI data for dashboard"""
    try:
        kpi_data = generate_kpi_data()
        serializer = KPISerializer(kpi_data, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error generating KPI data: {str(e)}")
        return Response(
            {'error': f'Failed to generate KPI data: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report(request):
    """Generate a report from template"""
    try:
        template_id = request.data.get('template_id')
        parameters = request.data.get('parameters', {})
        
        if not template_id:
            return Response(
                {'error': 'Template ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            template = ReportTemplate.objects.get(id=template_id)
        except ReportTemplate.DoesNotExist:
            return Response(
                {'error': 'Template not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create generated report
        report = GeneratedReport.objects.create(
            template=template,
            name=f"{template.name} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            parameters=parameters,
            generated_by=request.user,
            status='processing'
        )
        
        # Generate report data (this would be implemented based on template configuration)
        # For now, return mock data
        report.data = {
            'summary': 'Report generated successfully',
            'data': [],
            'generated_at': timezone.now().isoformat()
        }
        report.status = 'completed'
        report.completed_at = timezone.now()
        report.save()
        
        serializer = GeneratedReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return Response(
            {'error': f'Failed to generate report: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_export(request):
    """Request data export"""
    try:
        export_type = request.data.get('export_type')
        data_source = request.data.get('data_source')
        filters = request.data.get('filters', {})
        name = request.data.get('name', f"Export {timezone.now().strftime('%Y-%m-%d %H:%M')}")
        
        if not export_type or not data_source:
            return Response(
                {'error': 'Export type and data source are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create export request
        export = DataExport.objects.create(
            name=name,
            export_type=export_type,
            data_source=data_source,
            filters=filters,
            requested_by=request.user,
            status='processing'
        )
        
        # Process export (this would be implemented based on data source)
        # For now, mark as completed
        export.status = 'completed'
        export.completed_at = timezone.now()
        export.file_path = f"/exports/{export.id}.{export_type}"
        export.file_size = 1024  # Mock file size
        export.save()
        
        serializer = DataExportSerializer(export)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error requesting export: {str(e)}")
        return Response(
            {'error': f'Failed to request export: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def schedule_report(request):
    """Schedule a report"""
    try:
        template_id = request.data.get('template_id')
        frequency = request.data.get('frequency')
        parameters = request.data.get('parameters', {})
        recipients = request.data.get('recipients', [])
        name = request.data.get('name')
        
        if not all([template_id, frequency, name]):
            return Response(
                {'error': 'Template ID, frequency, and name are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            template = ReportTemplate.objects.get(id=template_id)
        except ReportTemplate.DoesNotExist:
            return Response(
                {'error': 'Template not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create scheduled report
        scheduled_report = ScheduledReport.objects.create(
            name=name,
            template=template,
            frequency=frequency,
            parameters=parameters,
            recipients=recipients,
            created_by=request.user
        )
        
        # Calculate next run time
        scheduled_report.next_run = calculate_next_run_time(frequency)
        scheduled_report.save()
        
        serializer = ScheduledReportSerializer(scheduled_report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error scheduling report: {str(e)}")
        return Response(
            {'error': f'Failed to schedule report: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def calculate_next_run_time(frequency):
    """Calculate next run time based on frequency"""
    now = timezone.now()
    
    if frequency == 'daily':
        return now + timedelta(days=1)
    elif frequency == 'weekly':
        return now + timedelta(weeks=1)
    elif frequency == 'monthly':
        return now + timedelta(days=30)
    elif frequency == 'quarterly':
        return now + timedelta(days=90)
    elif frequency == 'yearly':
        return now + timedelta(days=365)
    else:
        return now + timedelta(days=1)
