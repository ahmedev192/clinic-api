from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import LabResult, ResultAttachment
from .serializers import (
    LabResultSerializer, LabResultListSerializer, LabResultCreateSerializer,
    LabResultApprovalSerializer, LabResultUpdateSerializer, LabResultSearchSerializer,
    ResultAttachmentSerializer
)


class LabResultListCreateView(generics.ListCreateAPIView):
    """List and create lab results"""
    queryset = LabResult.objects.select_related(
        'sample__request_item__test__category', 'sample__request_item__request',
        'created_by', 'approved_by', 'rejected_by'
    ).prefetch_related('attachments').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'abnormality_flag', 'is_critical', 'is_approved', 'created_by']
    search_fields = [
        'sample__barcode', 'sample__tracking_code', 'sample__request_item__request__patient_name',
        'sample__request_item__request__patient_name_ar', 'sample__request_item__test__name_en',
        'sample__request_item__test__name_ar', 'comments_en', 'comments_ar'
    ]
    ordering_fields = ['created_at', 'completed_at', 'status', 'abnormality_flag']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LabResultListSerializer
        return LabResultCreateSerializer

    @extend_schema(
        summary=_("List lab results"),
        description=_("Get a list of all lab results with optional filtering and search"),
        tags=["Results"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Create lab result"),
        description=_("Create a new lab result for a sample"),
        tags=["Results"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LabResultDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a lab result"""
    queryset = LabResult.objects.select_related(
        'sample__request_item__test__category', 'sample__request_item__request',
        'created_by', 'approved_by', 'rejected_by'
    ).prefetch_related('attachments').all()
    serializer_class = LabResultSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return LabResultUpdateSerializer
        return LabResultSerializer

    @extend_schema(
        summary=_("Get lab result"),
        description=_("Retrieve a specific lab result by ID"),
        tags=["Results"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Update lab result"),
        description=_("Update a specific lab result"),
        tags=["Results"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary=_("Partially update lab result"),
        description=_("Partially update a specific lab result"),
        tags=["Results"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary=_("Delete lab result"),
        description=_("Delete a specific lab result"),
        tags=["Results"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary=_("Approve or reject result"),
    description=_("Approve or reject a lab result"),
    tags=["Results"],
    request=LabResultApprovalSerializer,
    responses={200: LabResultSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_reject_result(request, pk):
    """Approve or reject a lab result"""
    try:
        result = LabResult.objects.get(pk=pk)
    except LabResult.DoesNotExist:
        return Response(
            {'error': _('Lab result not found')}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = LabResultApprovalSerializer(data=request.data)
    if serializer.is_valid():
        action = serializer.validated_data['action']
        from django.utils import timezone
        
        if action == 'approve':
            result.is_approved = True
            result.approved_by = request.user
            result.approved_at = timezone.now()
            result.status = 'approved'
            result.rejection_reason_en = ''
            result.rejection_reason_ar = ''
            result.rejected_by = None
            result.rejected_at = None
        else:  # reject
            result.is_approved = False
            result.rejected_by = request.user
            result.rejected_at = timezone.now()
            result.status = 'rejected'
            result.rejection_reason_en = serializer.validated_data.get('rejection_reason_en', '')
            result.rejection_reason_ar = serializer.validated_data.get('rejection_reason_ar', '')
            result.approved_by = None
            result.approved_at = None
        
        result.save()
        
        response_serializer = LabResultSerializer(result)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary=_("Search results"),
    description=_("Search lab results by various criteria"),
    tags=["Results"],
    request=LabResultSearchSerializer,
    responses={200: LabResultListSerializer(many=True)}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_results(request):
    """Search lab results with advanced criteria"""
    serializer = LabResultSearchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    queryset = LabResult.objects.select_related(
        'sample__request_item__test__category', 'sample__request_item__request',
        'created_by', 'approved_by'
    ).all()
    
    # Apply search query
    if data.get('query'):
        query = data['query']
        queryset = queryset.filter(
            Q(sample__barcode__icontains=query) |
            Q(sample__tracking_code__icontains=query) |
            Q(sample__request_item__request__patient_name__icontains=query) |
            Q(sample__request_item__request__patient_name_ar__icontains=query) |
            Q(sample__request_item__test__name_en__icontains=query) |
            Q(sample__request_item__test__name_ar__icontains=query) |
            Q(comments_en__icontains=query) |
            Q(comments_ar__icontains=query)
        )
    
    # Apply filters
    if data.get('status'):
        queryset = queryset.filter(status=data['status'])
    
    if data.get('abnormality_flag'):
        queryset = queryset.filter(abnormality_flag=data['abnormality_flag'])
    
    if data.get('is_critical') is not None:
        queryset = queryset.filter(is_critical=data['is_critical'])
    
    if data.get('is_approved') is not None:
        queryset = queryset.filter(is_approved=data['is_approved'])
    
    if data.get('date_from'):
        queryset = queryset.filter(created_at__date__gte=data['date_from'])
    
    if data.get('date_to'):
        queryset = queryset.filter(created_at__date__lte=data['date_to'])
    
    # Order results
    queryset = queryset.order_by('-created_at')
    
    serializer = LabResultListSerializer(queryset, many=True)
    return Response(serializer.data)


@extend_schema(
    summary=_("Get critical results"),
    description=_("Get all critical lab results that need immediate attention"),
    tags=["Results"],
    responses={200: LabResultListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_critical_results(request):
    """Get all critical lab results"""
    results = LabResult.objects.filter(
        is_critical=True, 
        is_approved=False
    ).select_related(
        'sample__request_item__test__category', 'sample__request_item__request',
        'created_by', 'approved_by'
    ).order_by('-created_at')
    
    serializer = LabResultListSerializer(results, many=True)
    return Response(serializer.data)


@extend_schema(
    summary=_("Get pending approval results"),
    description=_("Get all lab results pending approval"),
    tags=["Results"],
    responses={200: LabResultListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_approval_results(request):
    """Get all results pending approval"""
    results = LabResult.objects.filter(
        status='final',
        is_approved=False
    ).select_related(
        'sample__request_item__test__category', 'sample__request_item__request',
        'created_by', 'approved_by'
    ).order_by('-created_at')
    
    serializer = LabResultListSerializer(results, many=True)
    return Response(serializer.data)


@extend_schema(
    summary=_("Get results by patient"),
    description=_("Get all lab results for a specific patient"),
    tags=["Results"],
    responses={200: LabResultListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_results_by_patient(request, patient_id):
    """Get all lab results for a specific patient"""
    results = LabResult.objects.filter(
        sample__request_item__request__patient_id=patient_id
    ).select_related(
        'sample__request_item__test__category', 'sample__request_item__request',
        'created_by', 'approved_by'
    ).order_by('-created_at')
    
    serializer = LabResultListSerializer(results, many=True)
    return Response(serializer.data)


class ResultAttachmentListCreateView(generics.ListCreateAPIView):
    """List and create result attachments"""
    queryset = ResultAttachment.objects.all()
    serializer_class = ResultAttachmentSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary=_("List result attachments"),
        description=_("Get attachments for a specific result"),
        tags=["Results"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Upload result attachment"),
        description=_("Upload an attachment for a lab result"),
        tags=["Results"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
