from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import LabRequest, LabRequestItem
from .serializers import (
    LabRequestSerializer, LabRequestCreateSerializer, LabRequestListSerializer,
    LabRequestStatusUpdateSerializer, LabRequestItemStatusUpdateSerializer
)


class LabRequestListCreateView(generics.ListCreateAPIView):
    """List and create lab requests"""
    queryset = LabRequest.objects.prefetch_related('items__test__category', 'created_by').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'urgency', 'patient_id', 'doctor_id']
    search_fields = [
        'request_number', 'patient_name', 'patient_name_ar', 
        'doctor_name', 'doctor_name_ar', 'clinical_notes_en', 'clinical_notes_ar'
    ]
    ordering_fields = ['request_date', 'status', 'urgency']
    ordering = ['-request_date']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LabRequestListSerializer
        return LabRequestCreateSerializer

    @extend_schema(
        summary=_("List lab requests"),
        description=_("Get a list of all lab requests with optional filtering and search"),
        tags=["Lab Requests"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Create lab request"),
        description=_("Create a new lab request with test items"),
        tags=["Lab Requests"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LabRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a lab request"""
    queryset = LabRequest.objects.prefetch_related('items__test__category', 'created_by').all()
    serializer_class = LabRequestSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary=_("Get lab request"),
        description=_("Retrieve a specific lab request by ID"),
        tags=["Lab Requests"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Update lab request"),
        description=_("Update a specific lab request"),
        tags=["Lab Requests"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary=_("Partially update lab request"),
        description=_("Partially update a specific lab request"),
        tags=["Lab Requests"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary=_("Delete lab request"),
        description=_("Delete a specific lab request"),
        tags=["Lab Requests"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary=_("Update request status"),
    description=_("Update the status of a lab request"),
    tags=["Lab Requests"],
    request=LabRequestStatusUpdateSerializer,
    responses={200: LabRequestSerializer}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_request_status(request, pk):
    """Update the status of a lab request"""
    try:
        lab_request = LabRequest.objects.get(pk=pk)
    except LabRequest.DoesNotExist:
        return Response(
            {'error': _('Lab request not found')}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = LabRequestStatusUpdateSerializer(data=request.data)
    if serializer.is_valid():
        lab_request.status = serializer.validated_data['status']
        
        # Update timestamps based on status
        from django.utils import timezone
        if lab_request.status == 'collected' and not lab_request.collection_date:
            lab_request.collection_date = timezone.now()
        elif lab_request.status == 'completed' and not lab_request.completion_date:
            lab_request.completion_date = timezone.now()
        
        lab_request.save()
        
        response_serializer = LabRequestSerializer(lab_request)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary=_("Update item status"),
    description=_("Update the status of a specific request item"),
    tags=["Lab Requests"],
    request=LabRequestItemStatusUpdateSerializer,
    responses={200: LabRequestItemStatusUpdateSerializer}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_item_status(request, item_id):
    """Update the status of a lab request item"""
    try:
        item = LabRequestItem.objects.get(pk=item_id)
    except LabRequestItem.DoesNotExist:
        return Response(
            {'error': _('Request item not found')}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = LabRequestItemStatusUpdateSerializer(data=request.data)
    if serializer.is_valid():
        for field, value in serializer.validated_data.items():
            setattr(item, field, value)
        item.save()
        
        return Response(LabRequestItemStatusUpdateSerializer(item).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary=_("Get requests by patient"),
    description=_("Get all lab requests for a specific patient"),
    tags=["Lab Requests"],
    responses={200: LabRequestListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_requests_by_patient(request, patient_id):
    """Get all lab requests for a specific patient"""
    requests = LabRequest.objects.filter(patient_id=patient_id).prefetch_related(
        'items__test__category'
    ).order_by('-request_date')
    
    serializer = LabRequestListSerializer(requests, many=True)
    return Response(serializer.data)


@extend_schema(
    summary=_("Get requests by doctor"),
    description=_("Get all lab requests created by a specific doctor"),
    tags=["Lab Requests"],
    responses={200: LabRequestListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_requests_by_doctor(request, doctor_id):
    """Get all lab requests created by a specific doctor"""
    requests = LabRequest.objects.filter(doctor_id=doctor_id).prefetch_related(
        'items__test__category'
    ).order_by('-request_date')
    
    serializer = LabRequestListSerializer(requests, many=True)
    return Response(serializer.data)


@extend_schema(
    summary=_("Get pending requests"),
    description=_("Get all pending lab requests for collection"),
    tags=["Lab Requests"],
    responses={200: LabRequestListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_requests(request):
    """Get all pending lab requests"""
    requests = LabRequest.objects.filter(status='pending').prefetch_related(
        'items__test__category'
    ).order_by('urgency', 'request_date')
    
    serializer = LabRequestListSerializer(requests, many=True)
    return Response(serializer.data)
