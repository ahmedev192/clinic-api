from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Sample, SampleCollection
from .serializers import (
    SampleSerializer, SampleListSerializer, SampleCollectionSerializer,
    SampleStatusUpdateSerializer, SampleCollectionUpdateSerializer, SampleSearchSerializer
)


class SampleListCreateView(generics.ListCreateAPIView):
    """List and create samples"""
    queryset = Sample.objects.select_related(
        'request_item__test__category', 'request_item__request', 'created_by'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'sample_type', 'collection_date', 'created_by']
    search_fields = [
        'barcode', 'tracking_code', 'collector_name', 'collector_name_ar',
        'request_item__request__patient_name', 'request_item__request__patient_name_ar'
    ]
    ordering_fields = ['collection_date', 'status', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SampleListSerializer
        return SampleSerializer

    @extend_schema(
        summary=_("List samples"),
        description=_("Get a list of all samples with optional filtering and search"),
        tags=["Samples"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Create sample"),
        description=_("Create a new sample for a request item"),
        tags=["Samples"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SampleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a sample"""
    queryset = Sample.objects.select_related(
        'request_item__test__category', 'request_item__request', 'created_by'
    ).all()
    serializer_class = SampleSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary=_("Get sample"),
        description=_("Retrieve a specific sample by ID"),
        tags=["Samples"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Update sample"),
        description=_("Update a specific sample"),
        tags=["Samples"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary=_("Partially update sample"),
        description=_("Partially update a specific sample"),
        tags=["Samples"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary=_("Delete sample"),
        description=_("Delete a specific sample"),
        tags=["Samples"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class SampleCollectionListCreateView(generics.ListCreateAPIView):
    """List and create sample collections"""
    queryset = SampleCollection.objects.all()
    serializer_class = SampleCollectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['collection_date', 'created_by']
    search_fields = ['collection_batch_id', 'collector_name', 'collector_name_ar', 'location']
    ordering_fields = ['collection_date', 'created_at']
    ordering = ['-collection_date']

    @extend_schema(
        summary=_("List sample collections"),
        description=_("Get a list of all sample collections"),
        tags=["Samples"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Create sample collection"),
        description=_("Create a new sample collection batch"),
        tags=["Samples"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(
    summary=_("Update sample status"),
    description=_("Update the status and details of a sample"),
    tags=["Samples"],
    request=SampleStatusUpdateSerializer,
    responses={200: SampleSerializer}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_sample_status(request, pk):
    """Update the status of a sample"""
    try:
        sample = Sample.objects.get(pk=pk)
    except Sample.DoesNotExist:
        return Response(
            {'error': _('Sample not found')}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = SampleStatusUpdateSerializer(data=request.data)
    if serializer.is_valid():
        for field, value in serializer.validated_data.items():
            if value is not None:
                setattr(sample, field, value)
        
        # Update collection date when status changes to collected
        if sample.status == 'pending' and serializer.validated_data.get('status') == 'collected':
            from django.utils import timezone
            sample.collection_date = timezone.now()
        
        sample.save()
        
        response_serializer = SampleSerializer(sample)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary=_("Search samples"),
    description=_("Search samples by barcode, tracking code, or other criteria"),
    tags=["Samples"],
    request=SampleSearchSerializer,
    responses={200: SampleListSerializer(many=True)}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_samples(request):
    """Search samples with advanced criteria"""
    serializer = SampleSearchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    queryset = Sample.objects.select_related(
        'request_item__test__category', 'request_item__request'
    ).all()
    
    # Apply search query
    if data.get('query'):
        query = data['query']
        queryset = queryset.filter(
            Q(barcode__icontains=query) |
            Q(tracking_code__icontains=query) |
            Q(request_item__request__patient_name__icontains=query) |
            Q(request_item__request__patient_name_ar__icontains=query) |
            Q(collector_name__icontains=query) |
            Q(collector_name_ar__icontains=query)
        )
    
    # Apply filters
    if data.get('status'):
        queryset = queryset.filter(status=data['status'])
    
    if data.get('sample_type'):
        queryset = queryset.filter(sample_type=data['sample_type'])
    
    if data.get('is_expired') is not None:
        from django.utils import timezone
        if data['is_expired']:
            queryset = queryset.filter(expiry_date__lt=timezone.now())
        else:
            queryset = queryset.filter(
                Q(expiry_date__isnull=True) | Q(expiry_date__gte=timezone.now())
            )
    
    # Order results
    queryset = queryset.order_by('-created_at')
    
    serializer = SampleListSerializer(queryset, many=True)
    return Response(serializer.data)


@extend_schema(
    summary=_("Get samples by status"),
    description=_("Get samples filtered by status"),
    tags=["Samples"],
    responses={200: SampleListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_samples_by_status(request, status):
    """Get samples by status"""
    if status not in [choice[0] for choice in Sample.STATUS_CHOICES]:
        return Response(
            {'error': _('Invalid status')}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    samples = Sample.objects.filter(status=status).select_related(
        'request_item__test__category', 'request_item__request'
    ).order_by('-created_at')
    
    serializer = SampleListSerializer(samples, many=True)
    return Response(serializer.data)


@extend_schema(
    summary=_("Get expired samples"),
    description=_("Get all expired samples"),
    tags=["Samples"],
    responses={200: SampleListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expired_samples(request):
    """Get all expired samples"""
    from django.utils import timezone
    
    samples = Sample.objects.filter(
        expiry_date__lt=timezone.now()
    ).select_related(
        'request_item__test__category', 'request_item__request'
    ).order_by('expiry_date')
    
    serializer = SampleListSerializer(samples, many=True)
    return Response(serializer.data)
