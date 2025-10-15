from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, FileResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import os

from .models import LabReport, ReportTemplate, ReportDelivery
from .serializers import (
    LabReportSerializer, LabReportListSerializer, LabReportCreateSerializer,
    LabReportGenerateSerializer, LabReportDeliverySerializer, LabReportSearchSerializer,
    ReportTemplateSerializer, ReportDeliverySerializer
)


class LabReportListCreateView(generics.ListCreateAPIView):
    """List and create lab reports"""
    queryset = LabReport.objects.select_related('lab_request', 'created_by').prefetch_related('deliveries').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'format', 'is_public', 'created_by']
    search_fields = [
        'report_number', 'title_en', 'title_ar', 'lab_request__request_number',
        'lab_request__patient_name', 'lab_request__patient_name_ar'
    ]
    ordering_fields = ['created_at', 'generated_at', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LabReportListSerializer
        return LabReportCreateSerializer

    @extend_schema(
        summary=_("List lab reports"),
        description=_("Get a list of all lab reports with optional filtering and search"),
        tags=["Reports"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Create lab report"),
        description=_("Create a new lab report"),
        tags=["Reports"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LabReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a lab report"""
    queryset = LabReport.objects.select_related('lab_request', 'created_by').prefetch_related('deliveries').all()
    serializer_class = LabReportSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary=_("Get lab report"),
        description=_("Retrieve a specific lab report by ID"),
        tags=["Reports"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Update lab report"),
        description=_("Update a specific lab report"),
        tags=["Reports"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary=_("Partially update lab report"),
        description=_("Partially update a specific lab report"),
        tags=["Reports"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary=_("Delete lab report"),
        description=_("Delete a specific lab report"),
        tags=["Reports"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ReportTemplateListCreateView(generics.ListCreateAPIView):
    """List and create report templates"""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_default', 'is_active', 'created_by']
    search_fields = ['name_en', 'name_ar', 'description_en', 'description_ar']
    ordering_fields = ['name_en', 'created_at']
    ordering = ['name_en']

    @extend_schema(
        summary=_("List report templates"),
        description=_("Get a list of all report templates"),
        tags=["Reports"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Create report template"),
        description=_("Create a new report template"),
        tags=["Reports"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ReportTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a report template"""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary=_("Get report template"),
        description=_("Retrieve a specific report template by ID"),
        tags=["Reports"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Update report template"),
        description=_("Update a specific report template"),
        tags=["Reports"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary=_("Partially update report template"),
        description=_("Partially update a specific report template"),
        tags=["Reports"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary=_("Delete report template"),
        description=_("Delete a specific report template"),
        tags=["Reports"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary=_("Generate report from request"),
    description=_("Generate a lab report from a lab request"),
    tags=["Reports"],
    request=LabReportGenerateSerializer,
    responses={201: LabReportSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report(request):
    """Generate a lab report from a lab request"""
    serializer = LabReportGenerateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    from apps.lab_requests.models import LabRequest
    
    try:
        lab_request = LabRequest.objects.get(id=data['lab_request_id'])
    except LabRequest.DoesNotExist:
        return Response(
            {'error': _('Lab request not found')}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if report already exists
    existing_report = LabReport.objects.filter(lab_request=lab_request).first()
    if existing_report:
        return Response(
            {'error': _('Report already exists for this request')}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create report
    report_data = {
        'lab_request': lab_request.id,
        'title_en': f"Lab Report - {lab_request.request_number}",
        'title_ar': f"تقرير المختبر - {lab_request.request_number}",
        'format': data['format'],
        'is_public': data['is_public'],
        'content_en': generate_report_content(lab_request, 'en'),
        'content_ar': generate_report_content(lab_request, 'ar'),
    }
    
    report_serializer = LabReportCreateSerializer(data=report_data, context={'request': request})
    if report_serializer.is_valid():
        report = report_serializer.save()
        return Response(LabReportSerializer(report).data, status=status.HTTP_201_CREATED)
    
    return Response(report_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def generate_report_content(lab_request, language):
    """Generate report content based on lab request"""
    # This is a simplified version - in production, you'd use a proper template engine
    content = {
        'header': {
            'clinic_name_en': 'Clinic Management System',
            'clinic_name_ar': 'نظام إدارة العيادة',
            'report_number': lab_request.request_number,
            'date': lab_request.request_date.strftime('%Y-%m-%d'),
        },
        'patient': {
            'name': lab_request.patient_name if language == 'en' else lab_request.patient_name_ar,
            'id': lab_request.patient_id,
        },
        'doctor': {
            'name': lab_request.doctor_name if language == 'en' else lab_request.doctor_name_ar,
            'id': lab_request.doctor_id,
        },
        'tests': []
    }
    
    # Add test results
    for item in lab_request.items.all():
        test_data = {
            'test_name': item.test.name_en if language == 'en' else item.test.name_ar,
            'test_code': item.test.code,
            'status': 'Completed' if item.is_completed else 'Pending',
        }
        
        # Add result if available
        if hasattr(item, 'sample') and hasattr(item.sample, 'result'):
            result = item.sample.result
            test_data['result'] = {
                'value': str(result.measured_value) if result.measured_value else '',
                'unit': result.unit,
                'normal_range': result.normal_range_text_en if language == 'en' else result.normal_range_text_ar,
                'abnormality': result.abnormality_flag,
                'comments': result.comments_en if language == 'en' else result.comments_ar,
            }
        
        content['tests'].append(test_data)
    
    return content


@extend_schema(
    summary=_("Download report file"),
    description=_("Download the generated report file"),
    tags=["Reports"],
    responses={200: OpenApiTypes.BINARY}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report(request, pk):
    """Download the report file"""
    try:
        report = LabReport.objects.get(pk=pk)
    except LabReport.DoesNotExist:
        return Response(
            {'error': _('Report not found')}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not report.file_path or not os.path.exists(report.file_path):
        return Response(
            {'error': _('Report file not found')}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Generate file if it doesn't exist
    if not report.file_path:
        report.generate_file()
    
    file_path = report.file_path
    file_name = f"{report.report_number}.{report.format}"
    
    response = FileResponse(
        open(file_path, 'rb'),
        content_type='application/pdf' if report.format == 'pdf' else 'text/html',
        as_attachment=True,
        filename=file_name
    )
    
    return response


@extend_schema(
    summary=_("Deliver report"),
    description=_("Deliver a report to a recipient"),
    tags=["Reports"],
    request=LabReportDeliverySerializer,
    responses={201: ReportDeliverySerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deliver_report(request, pk):
    """Deliver a report to a recipient"""
    try:
        report = LabReport.objects.get(pk=pk)
    except LabReport.DoesNotExist:
        return Response(
            {'error': _('Report not found')}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = LabReportDeliverySerializer(data=request.data)
    if serializer.is_valid():
        delivery_data = serializer.validated_data
        delivery_data['report'] = report.id
        
        delivery = ReportDelivery.objects.create(**delivery_data)
        
        # Update report status
        report.status = 'delivered'
        from django.utils import timezone
        report.delivered_at = timezone.now()
        report.save()
        
        return Response(ReportDeliverySerializer(delivery).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary=_("Search reports"),
    description=_("Search lab reports by various criteria"),
    tags=["Reports"],
    request=LabReportSearchSerializer,
    responses={200: LabReportListSerializer(many=True)}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_reports(request):
    """Search lab reports with advanced criteria"""
    serializer = LabReportSearchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    queryset = LabReport.objects.select_related('lab_request', 'created_by').all()
    
    # Apply search query
    if data.get('query'):
        query = data['query']
        queryset = queryset.filter(
            Q(report_number__icontains=query) |
            Q(title_en__icontains=query) |
            Q(title_ar__icontains=query) |
            Q(lab_request__request_number__icontains=query) |
            Q(lab_request__patient_name__icontains=query) |
            Q(lab_request__patient_name_ar__icontains=query)
        )
    
    # Apply filters
    if data.get('status'):
        queryset = queryset.filter(status=data['status'])
    
    if data.get('format'):
        queryset = queryset.filter(format=data['format'])
    
    if data.get('is_public') is not None:
        queryset = queryset.filter(is_public=data['is_public'])
    
    if data.get('date_from'):
        queryset = queryset.filter(created_at__date__gte=data['date_from'])
    
    if data.get('date_to'):
        queryset = queryset.filter(created_at__date__lte=data['date_to'])
    
    # Order results
    queryset = queryset.order_by('-created_at')
    
    serializer = LabReportListSerializer(queryset, many=True)
    return Response(serializer.data)
