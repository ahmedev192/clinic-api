"""
API Views for the Appointments & Scheduling module.

Provides comprehensive REST API endpoints for managing appointments,
doctor availability, waiting lists, and reminders.
"""

import logging
from datetime import datetime, date, time
from typing import Dict, List

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from rest_framework import status, generics, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Appointment, DoctorAvailability, WaitingList, Reminder, 
    AppointmentAuditLog, Doctor, Patient, ClinicSettings
)
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer, DoctorAvailabilitySerializer,
    WaitingListSerializer, ReminderSerializer, AppointmentAuditLogSerializer,
    ClinicSettingsSerializer, AppointmentSearchSerializer, AppointmentStatsSerializer,
    DoctorSerializer, PatientSerializer
)
from .services import (
    AppointmentService, DoctorAvailabilityService, 
    WaitingListService, ReminderService, SearchService
)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API responses."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointments.
    
    Provides CRUD operations for appointments with comprehensive filtering,
    searching, and business logic validation.
    """
    
    queryset = Appointment.objects.select_related(
        'patient__user', 'doctor__user', 'created_by', 'cancelled_by'
    ).all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'appointment_date', 'doctor', 'patient']
    search_fields = ['appointment_code', 'reason_for_visit__en', 'reason_for_visit__ar']
    ordering_fields = ['appointment_date', 'appointment_time', 'created_at']
    ordering = ['appointment_date', 'appointment_time']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return AppointmentCreateSerializer
        return AppointmentSerializer
    
    def perform_create(self, serializer):
        """Create appointment with business logic validation."""
        try:
            with transaction.atomic():
                # Use service to create appointment
                appointment = AppointmentService.create_appointment(
                    patient_id=serializer.validated_data['patient_id'],
                    doctor_id=serializer.validated_data['doctor_id'],
                    appointment_date=serializer.validated_data['appointment_date'],
                    appointment_time=serializer.validated_data['appointment_time'],
                    reason_for_visit=serializer.validated_data['reason_for_visit'],
                    duration_minutes=serializer.validated_data.get('duration_minutes', 30),
                    notes=serializer.validated_data.get('notes'),
                    created_by=self.request.user
                )
                serializer.instance = appointment
        except ValidationError as e:
            raise ValidationError(e.message)
        except Exception as e:
            logger.error(f"Failed to create appointment: {str(e)}")
            raise ValidationError("Failed to create appointment")
    
    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule an appointment."""
        try:
            appointment = self.get_object()
            new_date = datetime.strptime(request.data['appointment_date'], '%Y-%m-%d').date()
            new_time = datetime.strptime(request.data['appointment_time'], '%H:%M:%S').time()
            reason = request.data.get('reason', {})
            
            updated_appointment = AppointmentService.reschedule_appointment(
                appointment_id=str(appointment.id),
                new_date=new_date,
                new_time=new_time,
                rescheduled_by=request.user,
                reason=reason
            )
            
            serializer = self.get_serializer(updated_appointment)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Failed to reschedule appointment: {str(e)}")
            return Response({'error': 'Failed to reschedule appointment'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment."""
        try:
            appointment = self.get_object()
            reason = request.data.get('reason', {})
            
            updated_appointment = AppointmentService.cancel_appointment(
                appointment_id=str(appointment.id),
                cancelled_by=request.user,
                reason=reason
            )
            
            serializer = self.get_serializer(updated_appointment)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Failed to cancel appointment: {str(e)}")
            return Response({'error': 'Failed to cancel appointment'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark an appointment as completed."""
        try:
            appointment = self.get_object()
            notes = request.data.get('notes', {})
            
            updated_appointment = AppointmentService.mark_appointment_completed(
                appointment_id=str(appointment.id),
                completed_by=request.user,
                notes=notes
            )
            
            serializer = self.get_serializer(updated_appointment)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Failed to complete appointment: {str(e)}")
            return Response({'error': 'Failed to complete appointment'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search appointments with various filters."""
        try:
            search_serializer = AppointmentSearchSerializer(data=request.query_params)
            if not search_serializer.is_valid():
                return Response(search_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            appointments = SearchService.search_appointments(**search_serializer.validated_data)
            
            # Apply pagination
            page = self.paginate_queryset(appointments)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(appointments, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Failed to search appointments: {str(e)}")
            return Response({'error': 'Failed to search appointments'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get appointment statistics."""
        try:
            stats = AppointmentService.get_appointment_statistics()
            serializer = AppointmentStatsSerializer(stats)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Failed to get appointment statistics: {str(e)}")
            return Response({'error': 'Failed to get statistics'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments."""
        today = timezone.now().date()
        appointments = self.get_queryset().filter(appointment_date=today)
        
        page = self.paginate_queryset(appointments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments."""
        today = timezone.now().date()
        appointments = self.get_queryset().filter(
            appointment_date__gte=today,
            status__in=['scheduled', 'confirmed']
        )
        
        page = self.paginate_queryset(appointments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)


class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing doctor availability.
    
    Provides CRUD operations for doctor availability schedules
    with validation and conflict checking.
    """
    
    queryset = DoctorAvailability.objects.select_related('doctor__user').all()
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor', 'day_of_week', 'is_recurring', 'is_active']
    ordering_fields = ['day_of_week', 'start_time']
    ordering = ['day_of_week', 'start_time']
    
    def perform_create(self, serializer):
        """Create availability with validation."""
        try:
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.message)
    
    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """Get available time slots for a doctor on a specific date."""
        try:
            doctor_id = request.query_params.get('doctor_id')
            appointment_date = request.query_params.get('date')
            duration_minutes = int(request.query_params.get('duration_minutes', 30))
            
            if not doctor_id or not appointment_date:
                return Response({'error': 'doctor_id and date are required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            slots = DoctorAvailabilityService.get_available_slots(
                doctor_id, date_obj, duration_minutes
            )
            
            return Response(slots)
            
        except ValueError as e:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Failed to get available slots: {str(e)}")
            return Response({'error': 'Failed to get available slots'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def block_slot(self, request):
        """Block a specific time slot for a doctor."""
        try:
            doctor_id = request.data['doctor_id']
            date_str = request.data['date']
            start_time_str = request.data['start_time']
            end_time_str = request.data['end_time']
            reason = request.data.get('reason', {})
            
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
            
            availability = DoctorAvailabilityService.block_time_slot(
                doctor_id=doctor_id,
                date=date_obj,
                start_time=start_time,
                end_time=end_time,
                reason=reason,
                blocked_by=request.user
            )
            
            serializer = self.get_serializer(availability)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({'error': 'Invalid date/time format'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Failed to block time slot: {str(e)}")
            return Response({'error': 'Failed to block time slot'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WaitingListViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing waiting lists.
    
    Provides CRUD operations for waiting list entries
    with promotion to appointments functionality.
    """
    
    queryset = WaitingList.objects.select_related(
        'patient__user', 'doctor__user', 'contacted_by'
    ).all()
    serializer_class = WaitingListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor', 'patient', 'status', 'priority']
    ordering_fields = ['priority', 'created_at', 'preferred_date']
    ordering = ['-priority', 'created_at']
    
    def perform_create(self, serializer):
        """Create waiting list entry with validation."""
        try:
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.message)
    
    @action(detail=True, methods=['post'])
    def promote(self, request, pk=None):
        """Promote a waiting list entry to a confirmed appointment."""
        try:
            waiting_entry = self.get_object()
            appointment_date = datetime.strptime(request.data['appointment_date'], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(request.data['appointment_time'], '%H:%M:%S').time()
            
            appointment = WaitingListService.promote_from_waiting_list(
                waiting_list_id=str(waiting_entry.id),
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                promoted_by=request.user
            )
            
            appointment_serializer = AppointmentSerializer(appointment)
            return Response(appointment_serializer.data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': 'Invalid date/time format'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Failed to promote waiting list entry: {str(e)}")
            return Response({'error': 'Failed to promote waiting list entry'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def contact(self, request, pk=None):
        """Mark a waiting list entry as contacted."""
        try:
            waiting_entry = self.get_object()
            waiting_entry.status = 'contacted'
            waiting_entry.contacted_at = timezone.now()
            waiting_entry.contacted_by = request.user
            waiting_entry.save()
            
            serializer = self.get_serializer(waiting_entry)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to mark waiting list entry as contacted: {str(e)}")
            return Response({'error': 'Failed to mark as contacted'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointment reminders.
    
    Provides CRUD operations for reminders with scheduling functionality.
    """
    
    queryset = Reminder.objects.select_related('appointment__patient__user', 'appointment__doctor__user').all()
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['reminder_type', 'is_sent', 'delivery_status', 'appointment']
    ordering_fields = ['scheduled_time', 'created_at']
    ordering = ['scheduled_time']
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending reminders that need to be sent."""
        try:
            reminders = ReminderService.get_pending_reminders()
            
            page = self.paginate_queryset(reminders)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(reminders, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Failed to get pending reminders: {str(e)}")
            return Response({'error': 'Failed to get pending reminders'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def mark_sent(self, request, pk=None):
        """Mark a reminder as sent."""
        try:
            reminder = self.get_object()
            delivery_status = request.data.get('delivery_status', 'sent')
            
            updated_reminder = ReminderService.mark_reminder_sent(
                reminder_id=str(reminder.id),
                delivery_status=delivery_status
            )
            
            serializer = self.get_serializer(updated_reminder)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to mark reminder as sent: {str(e)}")
            return Response({'error': 'Failed to mark reminder as sent'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for doctors.
    
    Provides listing and retrieval of doctor information.
    """
    
    queryset = Doctor.objects.select_related('staff').filter(is_available=True)
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['staff__first_name_en', 'staff__last_name_en', 'staff__first_name_ar', 'staff__last_name_ar', 'professional_title_en', 'professional_title_ar']


class PatientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for patients.
    
    Provides listing and retrieval of patient information.
    """
    
    queryset = Patient.objects.filter(status='active')
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['first_name_en', 'last_name_en', 'first_name_ar', 'last_name_ar', 'patient_code']


class ClinicSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing clinic settings.
    
    Provides CRUD operations for clinic-wide settings.
    """
    
    queryset = ClinicSettings.objects.all()
    serializer_class = ClinicSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get or create clinic settings."""
        return ClinicSettings.get_settings()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_audit_log(request, appointment_id):
    """Get audit log for a specific appointment."""
    try:
        logs = AppointmentAuditLog.objects.filter(
            appointment_id=appointment_id
        ).order_by('-timestamp')
        
        serializer = AppointmentAuditLogSerializer(logs, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Failed to get appointment audit log: {str(e)}")
        return Response({'error': 'Failed to get audit log'}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'Appointments & Scheduling API'
    })
