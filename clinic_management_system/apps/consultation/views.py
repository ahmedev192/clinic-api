"""
Django REST Framework views for the Consultation & Clinical Notes Module.
Provides comprehensive API endpoints with filtering, searching, and multilingual support.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import Http404
import logging

from .models import (
    Consultation, Diagnosis, ConsultationDiagnosis, Prescription, PrescriptionItem,
    LabOrder, LabResult, Attachment, FollowUpNote, AuditLog
)
from .serializers import (
    ConsultationSerializer, ConsultationCreateSerializer, DiagnosisSerializer,
    ConsultationDiagnosisSerializer, PrescriptionSerializer, PrescriptionCreateSerializer,
    PrescriptionItemSerializer, LabOrderSerializer, LabOrderCreateSerializer,
    LabResultSerializer, AttachmentSerializer, FollowUpNoteSerializer,
    ConsultationSearchSerializer, AuditLogSerializer, ConsultationStatsSerializer
)
from .filters import ConsultationFilter, DiagnosisFilter, PrescriptionFilter, LabOrderFilter

logger = logging.getLogger(__name__)


class AuditMixin:
    """Mixin to handle audit logging for all views."""
    
    def perform_create(self, serializer):
        """Log creation action."""
        instance = serializer.save()
        self._log_action('create', instance)
        return instance
    
    def perform_update(self, serializer):
        """Log update action."""
        old_instance = self.get_object()
        old_values = self._get_object_values(old_instance)
        instance = serializer.save()
        new_values = self._get_object_values(instance)
        self._log_action('update', instance, old_values, new_values)
        return instance
    
    def perform_destroy(self, instance):
        """Log deletion action."""
        old_values = self._get_object_values(instance)
        self._log_action('delete', instance, old_values)
        return super().perform_destroy(instance)
    
    def _log_action(self, action, instance, old_values=None, new_values=None):
        """Create audit log entry."""
        try:
            AuditLog.objects.create(
                user=self.request.user,
                action=action,
                model_name=instance.__class__.__name__,
                object_id=str(instance.id),
                old_values=old_values,
                new_values=new_values,
                ip_address=self._get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
    
    def _get_object_values(self, instance):
        """Get object values for audit logging."""
        try:
            return {
                field.name: getattr(instance, field.name)
                for field in instance._meta.fields
                if field.name not in ['id', 'created', 'modified']
            }
        except Exception:
            return {}
    
    def _get_client_ip(self):
        """Get client IP address."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class ConsultationViewSet(AuditMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing consultations.
    Supports CRUD operations, filtering, searching, and statistics.
    """
    
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConsultationFilter
    search_fields = [
        'consultation_code', 'chief_complaint_en', 'chief_complaint_ar',
        'symptoms_en', 'symptoms_ar', 'assessment_notes_en', 'assessment_notes_ar'
    ]
    ordering_fields = ['consultation_date', 'created', 'modified']
    ordering = ['-consultation_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ConsultationCreateSerializer
        return ConsultationSerializer
    
    def get_queryset(self):
        """Filter consultations based on user permissions."""
        queryset = super().get_queryset()
        
        # Filter by patient if provided
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient__id=patient_id)
        
        # Filter by doctor if provided
        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            queryset = queryset.filter(doctor__id=doctor_id)
        
        return queryset.select_related('created_by', 'updated_by').prefetch_related(
            'diagnoses__diagnosis',
            'prescriptions__items',
            'lab_orders__results',
            'attachments',
            'follow_up_notes'
        )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search for consultations."""
        serializer = ConsultationSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        queryset = self.get_queryset()
        
        # Apply filters
        if data.get('patient'):
            queryset = queryset.filter(patient=data['patient'])
        
        if data.get('doctor_id'):
            queryset = queryset.filter(doctor__id=data['doctor_id'])
        
        if data.get('consultation_type'):
            queryset = queryset.filter(consultation_type=data['consultation_type'])
        
        if data.get('status'):
            queryset = queryset.filter(status=data['status'])
        
        if data.get('date_from'):
            queryset = queryset.filter(consultation_date__gte=data['date_from'])
        
        if data.get('date_to'):
            queryset = queryset.filter(consultation_date__lte=data['date_to'])
        
        if data.get('search_text'):
            search_text = data['search_text']
            queryset = queryset.filter(
                Q(consultation_code__icontains=search_text) |
                Q(chief_complaint_en__icontains=search_text) |
                Q(chief_complaint_ar__icontains=search_text) |
                Q(symptoms_en__icontains=search_text) |
                Q(symptoms_ar__icontains=search_text)
            )
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get consultation statistics."""
        queryset = self.get_queryset()
        
        stats = {
            'total_consultations': queryset.count(),
            'completed_consultations': queryset.filter(status='completed').count(),
            'draft_consultations': queryset.filter(status='draft').count(),
            'consultations_by_type': dict(
                queryset.values('consultation_type').annotate(
                    count=Count('id')
                ).values_list('consultation_type', 'count')
            ),
            'consultations_by_status': dict(
                queryset.values('status').annotate(
                    count=Count('id')
                ).values_list('status', 'count')
            ),
            'average_duration': queryset.filter(
                duration_minutes__isnull=False
            ).aggregate(avg=Avg('duration_minutes'))['avg'] or 0,
            'total_prescriptions': Prescription.objects.filter(
                consultation__in=queryset
            ).count(),
            'total_lab_orders': LabOrder.objects.filter(
                consultation__in=queryset
            ).count(),
            'total_attachments': Attachment.objects.filter(
                consultation__in=queryset
            ).count(),
        }
        
        serializer = ConsultationStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark consultation as completed."""
        consultation = self.get_object()
        if consultation.status == 'completed':
            return Response(
                {'error': 'Consultation is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consultation.status = 'completed'
        consultation.updated_by = request.user
        consultation.save()
        
        serializer = self.get_serializer(consultation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_diagnosis(self, request, pk=None):
        """Add diagnosis to consultation."""
        consultation = self.get_object()
        diagnosis_id = request.data.get('diagnosis_id')
        
        if not diagnosis_id:
            return Response(
                {'error': 'diagnosis_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            diagnosis = Diagnosis.objects.get(id=diagnosis_id)
        except Diagnosis.DoesNotExist:
            return Response(
                {'error': 'Diagnosis not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if diagnosis already exists
        if ConsultationDiagnosis.objects.filter(
            consultation=consultation,
            diagnosis=diagnosis
        ).exists():
            return Response(
                {'error': 'Diagnosis already added to this consultation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consultation_diagnosis = ConsultationDiagnosis.objects.create(
            consultation=consultation,
            diagnosis=diagnosis,
            status=request.data.get('status', 'primary'),
            notes_en=request.data.get('notes_en', ''),
            notes_ar=request.data.get('notes_ar', ''),
            onset_date=request.data.get('onset_date'),
            is_resolved=request.data.get('is_resolved', False)
        )
        
        serializer = ConsultationDiagnosisSerializer(consultation_diagnosis)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DiagnosisViewSet(AuditMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing diagnoses.
    Supports CRUD operations and filtering.
    """
    
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DiagnosisFilter
    search_fields = ['name_en', 'name_ar', 'diagnosis_code', 'category']
    ordering_fields = ['name_en', 'name_ar', 'created']
    ordering = ['name_en']
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get diagnoses grouped by category."""
        categories = Diagnosis.objects.values('category').distinct()
        result = {}
        
        for category in categories:
            cat_name = category['category']
            diagnoses = Diagnosis.objects.filter(category=cat_name)
            serializer = self.get_serializer(diagnoses, many=True)
            result[cat_name] = serializer.data
        
        return Response(result)


class PrescriptionViewSet(AuditMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing prescriptions.
    Supports CRUD operations and filtering.
    """
    
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PrescriptionFilter
    search_fields = ['prescription_code', 'notes_en', 'notes_ar']
    ordering_fields = ['prescribed_date', 'created']
    ordering = ['-prescribed_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return PrescriptionCreateSerializer
        return PrescriptionSerializer
    
    def get_queryset(self):
        """Filter prescriptions by consultation if provided."""
        queryset = super().get_queryset()
        consultation_id = self.request.query_params.get('consultation_id')
        
        if consultation_id:
            queryset = queryset.filter(consultation_id=consultation_id)
        
        return queryset.select_related('consultation').prefetch_related('items')
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add item to prescription."""
        prescription = self.get_object()
        
        if prescription.status == 'completed':
            return Response(
                {'error': 'Cannot add items to completed prescription'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PrescriptionItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(prescription=prescription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def send_to_pharmacy(self, request, pk=None):
        """Send prescription to pharmacy module."""
        prescription = self.get_object()
        
        if prescription.status != 'active':
            return Response(
                {'error': 'Only active prescriptions can be sent to pharmacy'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update pharmacy status
        prescription.pharmacy_status = 'sent'
        prescription.pharmacy_notes = request.data.get('pharmacy_notes', '')
        prescription.save()
        
        # Here you would integrate with the Pharmacy Module
        # For now, we just update the status
        
        serializer = self.get_serializer(prescription)
        return Response(serializer.data)


class LabOrderViewSet(AuditMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing lab orders.
    Supports CRUD operations and filtering.
    """
    
    queryset = LabOrder.objects.all()
    serializer_class = LabOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LabOrderFilter
    search_fields = ['order_code', 'test_name_en', 'test_name_ar']
    ordering_fields = ['ordered_date', 'created']
    ordering = ['-ordered_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return LabOrderCreateSerializer
        return LabOrderSerializer
    
    def get_queryset(self):
        """Filter lab orders by consultation if provided."""
        queryset = super().get_queryset()
        consultation_id = self.request.query_params.get('consultation_id')
        
        if consultation_id:
            queryset = queryset.filter(consultation_id=consultation_id)
        
        return queryset.select_related('consultation').prefetch_related('results')
    
    @action(detail=True, methods=['post'])
    def add_result(self, request, pk=None):
        """Add result to lab order."""
        lab_order = self.get_object()
        
        serializer = LabResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(lab_order=lab_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def send_to_lab(self, request, pk=None):
        """Send lab order to laboratory module."""
        lab_order = self.get_object()
        
        if lab_order.status != 'pending':
            return Response(
                {'error': 'Only pending lab orders can be sent to laboratory'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update lab status
        lab_order.lab_status = 'sent'
        lab_order.lab_reference = request.data.get('lab_reference', '')
        lab_order.save()
        
        # Here you would integrate with the Laboratory Module
        # For now, we just update the status
        
        serializer = self.get_serializer(lab_order)
        return Response(serializer.data)


class AttachmentViewSet(AuditMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing attachments.
    Supports CRUD operations and file uploads.
    """
    
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title_en', 'title_ar', 'file_name']
    ordering_fields = ['created', 'file_name']
    ordering = ['-created']
    
    def get_queryset(self):
        """Filter attachments by consultation if provided."""
        queryset = super().get_queryset()
        consultation_id = self.request.query_params.get('consultation_id')
        
        if consultation_id:
            queryset = queryset.filter(consultation_id=consultation_id)
        
        return queryset.select_related('consultation', 'uploaded_by')
    
    def perform_create(self, serializer):
        """Set uploaded_by and file_size on creation."""
        file = self.request.FILES.get('file')
        if file:
            serializer.save(
                uploaded_by=self.request.user,
                file_size=file.size,
                file_name=file.name
            )
        else:
            serializer.save(uploaded_by=self.request.user)


class FollowUpNoteViewSet(AuditMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing follow-up notes.
    Supports CRUD operations and filtering.
    """
    
    queryset = FollowUpNote.objects.all()
    serializer_class = FollowUpNoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content_en', 'content_ar']
    ordering_fields = ['note_date', 'created']
    ordering = ['-note_date']
    
    def get_queryset(self):
        """Filter follow-up notes by consultation if provided."""
        queryset = super().get_queryset()
        consultation_id = self.request.query_params.get('consultation_id')
        
        if consultation_id:
            queryset = queryset.filter(consultation_id=consultation_id)
        
        return queryset.select_related('consultation', 'created_by')
    
    def perform_create(self, serializer):
        """Set created_by on creation."""
        serializer.save(created_by=self.request.user)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs.
    Read-only access for compliance and security.
    """
    
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created', 'action', 'model_name']
    ordering = ['-created']
    
    def get_queryset(self):
        """Filter audit logs based on user permissions."""
        queryset = super().get_queryset()
        
        # Filter by model name if provided
        model_name = self.request.query_params.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        
        # Filter by action if provided
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by user if provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.select_related('user')
