from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import TestCategory, LabTest
from .serializers import (
    TestCategorySerializer, LabTestSerializer, 
    LabTestListSerializer, LabTestSearchSerializer
)


class TestCategoryListCreateView(generics.ListCreateAPIView):
    """List and create test categories"""
    queryset = TestCategory.objects.all()
    serializer_class = TestCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name_en', 'name_ar', 'description_en', 'description_ar']
    ordering_fields = ['name_en', 'name_ar', 'created_at']
    ordering = ['name_en']

    @extend_schema(
        summary=_("List test categories"),
        description=_("Get a list of all test categories with optional filtering and search"),
        tags=["Lab Tests"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Create test category"),
        description=_("Create a new test category"),
        tags=["Lab Tests"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TestCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a test category"""
    queryset = TestCategory.objects.all()
    serializer_class = TestCategorySerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary=_("Get test category"),
        description=_("Retrieve a specific test category by ID"),
        tags=["Lab Tests"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Update test category"),
        description=_("Update a specific test category"),
        tags=["Lab Tests"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary=_("Partially update test category"),
        description=_("Partially update a specific test category"),
        tags=["Lab Tests"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary=_("Delete test category"),
        description=_("Delete a specific test category"),
        tags=["Lab Tests"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class LabTestListCreateView(generics.ListCreateAPIView):
    """List and create lab tests"""
    queryset = LabTest.objects.select_related('category', 'created_by').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'sample_type']
    search_fields = ['name_en', 'name_ar', 'code', 'description_en', 'description_ar']
    ordering_fields = ['name_en', 'name_ar', 'price', 'created_at']
    ordering = ['category', 'name_en']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LabTestListSerializer
        return LabTestSerializer

    @extend_schema(
        summary=_("List lab tests"),
        description=_("Get a list of all lab tests with optional filtering and search"),
        tags=["Lab Tests"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Create lab test"),
        description=_("Create a new lab test"),
        tags=["Lab Tests"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LabTestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a lab test"""
    queryset = LabTest.objects.select_related('category', 'created_by').all()
    serializer_class = LabTestSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary=_("Get lab test"),
        description=_("Retrieve a specific lab test by ID"),
        tags=["Lab Tests"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary=_("Update lab test"),
        description=_("Update a specific lab test"),
        tags=["Lab Tests"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary=_("Partially update lab test"),
        description=_("Partially update a specific lab test"),
        tags=["Lab Tests"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary=_("Delete lab test"),
        description=_("Delete a specific lab test"),
        tags=["Lab Tests"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary=_("Search lab tests"),
    description=_("Search lab tests by name, code, or other criteria"),
    tags=["Lab Tests"],
    request=LabTestSearchSerializer,
    responses={200: LabTestListSerializer(many=True)}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_tests(request):
    """Search lab tests with advanced criteria"""
    serializer = LabTestSearchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    queryset = LabTest.objects.select_related('category').all()
    
    # Apply search query
    if data.get('query'):
        query = data['query']
        queryset = queryset.filter(
            Q(name_en__icontains=query) |
            Q(name_ar__icontains=query) |
            Q(code__icontains=query) |
            Q(description_en__icontains=query) |
            Q(description_ar__icontains=query)
        )
    
    # Apply filters
    if data.get('category'):
        queryset = queryset.filter(category_id=data['category'])
    
    if data.get('is_active') is not None:
        queryset = queryset.filter(is_active=data['is_active'])
    
    # Order results
    queryset = queryset.order_by('category', 'name_en')
    
    serializer = LabTestListSerializer(queryset, many=True)
    return Response(serializer.data)


@extend_schema(
    summary=_("Get active lab tests"),
    description=_("Get a list of all active lab tests for selection purposes"),
    tags=["Lab Tests"],
    responses={200: LabTestListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_tests(request):
    """Get all active lab tests for selection"""
    queryset = LabTest.objects.filter(is_active=True).select_related('category').order_by('category', 'name_en')
    serializer = LabTestListSerializer(queryset, many=True)
    return Response(serializer.data)
