"""
Patient Management API Views

This module provides comprehensive API views for patient management operations.
Includes CRUD operations, search, filtering, and export functionality.
"""

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import (
    Patient, MedicalHistory, Allergy, ChronicCondition, 
    PatientDocument, PatientSearchLog
)
from .serializers import (
    PatientSerializer, PatientListSerializer, PatientDetailSerializer,
    PatientCreateSerializer, MedicalHistorySerializer, AllergySerializer,
    ChronicConditionSerializer, PatientDocumentSerializer, PatientSearchLogSerializer
)
from .filters import (
    PatientFilter, MedicalHistoryFilter, AllergyFilter,
    ChronicConditionFilter, PatientDocumentFilter
)
from .permissions import (
    CanViewPatientData, CanEditPatientData, CanDeletePatientData,
    CanAccessMedicalHistory, CanUploadDocuments, CanExportData
)
from .utils import get_patient_statistics, export_patients_to_csv
from audit_logs.models import PatientAccessLog, DataExportLog


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Patient model with comprehensive CRUD operations.
    """
    
    queryset = Patient.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated, CanViewPatientData]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PatientFilter
    search_fields = [
        'patient_code', 'first_name_en', 'first_name_ar', 'last_name_en', 
        'last_name_ar', 'national_id', 'phone_number', 'email'
    ]
    ordering_fields = ['created_at', 'updated_at', 'patient_code', 'first_name_en', 'last_name_en']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return PatientListSerializer
        elif self.action == 'create':
            return PatientCreateSerializer
        elif self.action == 'retrieve':
            return PatientDetailSerializer
        else:
            return PatientSerializer
    
    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated, CanViewPatientData]
        elif self.action in ['create', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, CanEditPatientData]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, CanDeletePatientData]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set created_by and updated_by fields"""
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Set updated_by field"""
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete the patient"""
        instance.soft_delete(self.request.user)
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-staff users can only see patients they created
        if not self.request.user.is_staff:
            user_groups = self.request.user.groups.values_list('name', flat=True)
            if 'administrators' not in user_groups:
                queryset = queryset.filter(created_by=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def access_log(self, request, pk=None):
        """Get access log for a specific patient"""
        patient = self.get_object()
        
        # Log the access
        PatientAccessLog.objects.create(
            patient=patient,
            user=request.user,
            access_type='view',
            reason='Viewed patient access log',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            request_path=request.path
        )
        
        # Get access logs
        access_logs = PatientAccessLog.objects.filter(patient=patient).order_by('-timestamp')[:50]
        serializer = PatientSearchLogSerializer(access_logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get patient statistics"""
        stats = get_patient_statistics()
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search with logging"""
        query = request.query_params.get('q', '')
        filters = dict(request.query_params)
        
        # Log the search
        queryset = self.filter_queryset(self.get_queryset())
        results_count = queryset.count()
        
        PatientSearchLog.objects.create(
            searcher=request.user,
            search_query=query,
            search_filters=filters,
            results_count=results_count
        )
        
        # Return search results
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': results_count,
            'query': query,
            'filters': filters
        })
    
    @action(detail=False, methods=['get'], permission_classes=[CanExportData])
    def export(self, request):
        """Export patients to CSV"""
        queryset = self.filter_queryset(self.get_queryset())
        include_medical_data = request.query_params.get('include_medical', 'false').lower() == 'true'
        
        # Log the export
        csv_data = export_patients_to_csv(queryset, include_medical_data)
        
        DataExportLog.objects.create(
            user=request.user,
            export_type='patient_list',
            format='csv',
            record_count=queryset.count(),
            file_size=len(csv_data.encode('utf-8')),
            filters_applied=dict(request.query_params),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="patients_export.csv"'
        return response
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a soft-deleted patient"""
        patient = get_object_or_404(Patient, pk=pk, is_deleted=True)
        
        patient.is_deleted = False
        patient.deleted_at = None
        patient.deleted_by = None
        patient.status = 'active'
        patient.updated_by = request.user
        patient.save()
        
        serializer = self.get_serializer(patient)
        return Response(serializer.data)


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MedicalHistory model.
    """
    
    queryset = MedicalHistory.objects.all()
    serializer_class = MedicalHistorySerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessMedicalHistory]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MedicalHistoryFilter
    search_fields = ['title_en', 'title_ar', 'description_en', 'description_ar', 'diagnosis_code']
    ordering_fields = ['event_date', 'created_at', 'title_en']
    ordering = ['-event_date', '-created_at']
    
    def perform_create(self, serializer):
        """Set created_by and updated_by fields"""
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Set updated_by field"""
        serializer.save(updated_by=self.request.user)
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-staff users can only see medical history for patients they created
        if not self.request.user.is_staff:
            user_groups = self.request.user.groups.values_list('name', flat=True)
            if 'administrators' not in user_groups:
                queryset = queryset.filter(patient__created_by=self.request.user)
        
        return queryset


class AllergyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Allergy model.
    """
    
    queryset = Allergy.objects.all()
    serializer_class = AllergySerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessMedicalHistory]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AllergyFilter
    search_fields = ['allergen_en', 'allergen_ar', 'description_en', 'description_ar', 'symptoms']
    ordering_fields = ['severity', 'allergen_en', 'created_at']
    ordering = ['-severity', 'allergen_en']
    
    def perform_create(self, serializer):
        """Set created_by and updated_by fields"""
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Set updated_by field"""
        serializer.save(updated_by=self.request.user)
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-staff users can only see allergies for patients they created
        if not self.request.user.is_staff:
            user_groups = self.request.user.groups.values_list('name', flat=True)
            if 'administrators' not in user_groups:
                queryset = queryset.filter(patient__created_by=self.request.user)
        
        return queryset


class ChronicConditionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ChronicCondition model.
    """
    
    queryset = ChronicCondition.objects.all()
    serializer_class = ChronicConditionSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessMedicalHistory]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ChronicConditionFilter
    search_fields = ['condition_name_en', 'condition_name_ar', 'description_en', 'description_ar', 'icd_code']
    ordering_fields = ['severity', 'condition_name_en', 'diagnosis_date']
    ordering = ['-severity', 'condition_name_en']
    
    def perform_create(self, serializer):
        """Set created_by and updated_by fields"""
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Set updated_by field"""
        serializer.save(updated_by=self.request.user)
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-staff users can only see chronic conditions for patients they created
        if not self.request.user.is_staff:
            user_groups = self.request.user.groups.values_list('name', flat=True)
            if 'administrators' not in user_groups:
                queryset = queryset.filter(patient__created_by=self.request.user)
        
        return queryset


class PatientDocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PatientDocument model.
    """
    
    queryset = PatientDocument.objects.all()
    serializer_class = PatientDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, CanUploadDocuments]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PatientDocumentFilter
    search_fields = ['title_en', 'title_ar', 'description_en', 'description_ar']
    ordering_fields = ['upload_date', 'title_en', 'file_size']
    ordering = ['-upload_date']
    parser_classes = [MultiPartParser, FormParser]
    
    def perform_create(self, serializer):
        """Set uploaded_by field"""
        serializer.save(uploaded_by=self.request.user)
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-staff users can only see documents for patients they created
        if not self.request.user.is_staff:
            user_groups = self.request.user.groups.values_list('name', flat=True)
            if 'administrators' not in user_groups:
                queryset = queryset.filter(patient__created_by=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a document"""
        document = self.get_object()
        
        document.is_verified = True
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.save()
        
        serializer = self.get_serializer(document)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unverify(self, request, pk=None):
        """Unverify a document"""
        document = self.get_object()
        
        document.is_verified = False
        document.verified_by = None
        document.verified_at = None
        document.save()
        
        serializer = self.get_serializer(document)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """Get documents for a specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response({'error': 'patient_id parameter is required'}, status=400)
        
        queryset = self.get_queryset().filter(patient_id=patient_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PatientSearchLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for PatientSearchLog model (read-only).
    """
    
    queryset = PatientSearchLog.objects.all()
    serializer_class = PatientSearchLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['searcher', 'search_timestamp']
    ordering_fields = ['search_timestamp']
    ordering = ['-search_timestamp']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-staff users can only see their own search logs
        if not self.request.user.is_staff:
            queryset = queryset.filter(searcher=self.request.user)
        
        return queryset
