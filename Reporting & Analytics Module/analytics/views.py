"""
Views for the Analytics module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Sum, Avg, Count, Min, Max
from django.utils import timezone
from django.http import HttpResponse, FileResponse
from django.core.cache import cache
from django.conf import settings
import pandas as pd
import json
import io
import os
from datetime import datetime, timedelta
from .models import ReportTemplate, ReportQuery, ReportResult, DataSource, ReportSchedule
from .serializers import (
    ReportTemplateSerializer, ReportQuerySerializer, ReportResultSerializer,
    DataSourceSerializer, ReportScheduleSerializer, FinancialReportSerializer,
    DemographicReportSerializer, DoctorPerformanceSerializer, AppointmentStatsSerializer,
    CustomReportSerializer, ExportRequestSerializer
)
from .tasks import generate_report_task, send_scheduled_report_task
from .utils import (
    generate_financial_report, generate_demographic_report,
    generate_doctor_performance_report, generate_appointment_stats_report,
    generate_custom_report, export_to_csv, export_to_excel, export_to_pdf
)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for ReportTemplate model."""
    queryset = ReportTemplate.objects.filter(is_active=True)
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['report_type', 'created_by']
    search_fields = ['name', 'name_ar', 'description', 'description_ar']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a report template."""
        template = self.get_object()
        new_template = ReportTemplate.objects.create(
            name=f"{template.name} (Copy)",
            name_ar=f"{template.name_ar} (نسخة)" if template.name_ar else "",
            description=template.description,
            description_ar=template.description_ar,
            report_type=template.report_type,
            modules=template.modules,
            filters=template.filters,
            date_range=template.date_range,
            aggregation_fields=template.aggregation_fields,
            group_by_fields=template.group_by_fields,
            export_formats=template.export_formats,
            include_charts=template.include_charts,
            created_by=request.user
        )
        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReportQueryViewSet(viewsets.ModelViewSet):
    """ViewSet for ReportQuery model."""
    queryset = ReportQuery.objects.all()
    serializer_class = ReportQuerySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'report_type', 'created_by']
    search_fields = ['name', 'name_ar']
    ordering_fields = ['created_at', 'started_at', 'completed_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a report query."""
        query = self.get_object()
        if query.status == 'processing':
            return Response(
                {'error': 'Query is already being processed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start background task
        task = generate_report_task.delay(query.id)
        query.status = 'processing'
        query.started_at = timezone.now()
        query.save()
        
        return Response({
            'message': 'Report generation started.',
            'task_id': task.id
        })
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get the status of a report query."""
        query = self.get_object()
        return Response({
            'status': query.status,
            'started_at': query.started_at,
            'completed_at': query.completed_at,
            'error_message': query.error_message,
            'retry_count': query.retry_count
        })


class ReportResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ReportResult model."""
    queryset = ReportResult.objects.all()
    serializer_class = ReportResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['query__created_by', 'query__report_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class DataSourceViewSet(viewsets.ModelViewSet):
    """ViewSet for DataSource model."""
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['source_type', 'is_active']
    search_fields = ['name', 'name_ar']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for ReportSchedule model."""
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['frequency', 'is_active', 'created_by']
    search_fields = ['name', 'name_ar']
    ordering_fields = ['created_at', 'next_run']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)


class FinancialReportViewSet(viewsets.GenericViewSet):
    """ViewSet for financial reports."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate financial report."""
        serializer = FinancialReportSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Check cache first
            cache_key = f"financial_report_{hash(str(data))}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return Response(cached_result)
            
            # Generate report
            report_data = generate_financial_report(
                date_from=data['date_from'],
                date_to=data['date_to'],
                department=data.get('department'),
                payment_type=data.get('payment_type')
            )
            
            # Cache for 1 hour
            cache.set(cache_key, report_data, 3600)
            
            return Response(report_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get financial summary for dashboard."""
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        date_to = timezone.now()
        date_from = date_to - timedelta(days=days)
        
        # Generate summary
        summary = generate_financial_report(
            date_from=date_from,
            date_to=date_to
        )
        
        return Response(summary.get('summary', {}))


class DemographicReportViewSet(viewsets.GenericViewSet):
    """ViewSet for demographic reports."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate demographic report."""
        serializer = DemographicReportSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Check cache first
            cache_key = f"demographic_report_{hash(str(data))}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return Response(cached_result)
            
            # Generate report
            report_data = generate_demographic_report(
                date_from=data['date_from'],
                date_to=data['date_to'],
                include_gender=data['include_gender'],
                include_age_groups=data['include_age_groups'],
                include_location=data['include_location'],
                include_visit_frequency=data['include_visit_frequency']
            )
            
            # Cache for 2 hours
            cache.set(cache_key, report_data, 7200)
            
            return Response(report_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorPerformanceViewSet(viewsets.GenericViewSet):
    """ViewSet for doctor performance reports."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate doctor performance report."""
        serializer = DoctorPerformanceSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Check cache first
            cache_key = f"doctor_performance_{hash(str(data))}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return Response(cached_result)
            
            # Generate report
            report_data = generate_doctor_performance_report(
                date_from=data['date_from'],
                date_to=data['date_to'],
                doctor_ids=data.get('doctor_ids'),
                include_revenue=data['include_revenue'],
                include_consultation_time=data['include_consultation_time'],
                include_satisfaction=data['include_satisfaction']
            )
            
            # Cache for 1 hour
            cache.set(cache_key, report_data, 3600)
            
            return Response(report_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentStatsViewSet(viewsets.GenericViewSet):
    """ViewSet for appointment statistics reports."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate appointment statistics report."""
        serializer = AppointmentStatsSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Check cache first
            cache_key = f"appointment_stats_{hash(str(data))}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return Response(cached_result)
            
            # Generate report
            report_data = generate_appointment_stats_report(
                date_from=data['date_from'],
                date_to=data['date_to'],
                group_by=data['group_by'],
                include_no_shows=data['include_no_shows'],
                include_cancellations=data['include_cancellations'],
                include_peak_hours=data['include_peak_hours']
            )
            
            # Cache for 30 minutes
            cache.set(cache_key, report_data, 1800)
            
            return Response(report_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomReportViewSet(viewsets.GenericViewSet):
    """ViewSet for custom report builder."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate custom report."""
        serializer = CustomReportSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Check cache first
            cache_key = f"custom_report_{hash(str(data))}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return Response(cached_result)
            
            # Generate report
            report_data = generate_custom_report(
                modules=data['modules'],
                filters=data.get('filters', {}),
                date_from=data['date_from'],
                date_to=data['date_to'],
                group_by_fields=data.get('group_by_fields', []),
                aggregation_fields=data.get('aggregation_fields, {}')
            )
            
            # Save template if requested
            if data.get('save_template'):
                template = ReportTemplate.objects.create(
                    name=data['name'],
                    name_ar=data.get('name_ar', ''),
                    description=f"Custom report generated on {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                    report_type='custom',
                    modules=data['modules'],
                    filters=data.get('filters', {}),
                    date_range={'from': data['date_from'], 'to': data['date_to']},
                    group_by_fields=data.get('group_by_fields', []),
                    aggregation_fields=data.get('aggregation_fields', {}),
                    export_formats=data['export_formats'],
                    created_by=request.user
                )
                report_data['template_id'] = template.id
            
            # Cache for 1 hour
            cache.set(cache_key, report_data, 3600)
            
            return Response(report_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExportViewSet(viewsets.GenericViewSet):
    """ViewSet for report exports."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate export file."""
        serializer = ExportRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            try:
                query = ReportQuery.objects.get(id=data['query_id'])
                result = query.reportresult
                
                if data['format'] == 'csv':
                    file_content = export_to_csv(
                        result.data,
                        include_headers_ar=data['include_headers_ar'],
                        include_headers_en=data['include_headers_en']
                    )
                    response = HttpResponse(file_content, content_type='text/csv')
                    response['Content-Disposition'] = f'attachment; filename="report_{query.id}.csv"'
                    return response
                
                elif data['format'] == 'excel':
                    file_content = export_to_excel(
                        result.data,
                        include_headers_ar=data['include_headers_ar'],
                        include_headers_en=data['include_headers_en']
                    )
                    response = HttpResponse(
                        file_content,
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    response['Content-Disposition'] = f'attachment; filename="report_{query.id}.xlsx"'
                    return response
                
                elif data['format'] == 'pdf':
                    file_content = export_to_pdf(
                        result.data,
                        query.name,
                        include_headers_ar=data['include_headers_ar'],
                        include_headers_en=data['include_headers_en']
                    )
                    response = HttpResponse(file_content, content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="report_{query.id}.pdf"'
                    return response
                
            except ReportQuery.DoesNotExist:
                return Response(
                    {'error': 'Query not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
