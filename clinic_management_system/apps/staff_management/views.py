"""
Views for Staff Management API
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from apps.accounts.models import User
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Role, Specialization, Staff, Doctor, Schedule, 
    Compensation, StaffAuditLog
)
from .serializers import (
    RoleSerializer, SpecializationSerializer, StaffSerializer, 
    StaffListSerializer, StaffCreateSerializer, DoctorSerializer,
    ScheduleSerializer, CompensationSerializer, StaffAuditLogSerializer,
    StaffSearchSerializer, StaffStatsSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin, IsStaffOrAdmin
from .filters import StaffFilter, DoctorFilter, ScheduleFilter


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing staff roles
    """
    queryset = Role.objects.filter(is_removed=False)
    serializer_class = RoleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name_en', 'name_ar']
    filterset_fields = ['is_active']
    ordering_fields = ['name_en', 'created']
    ordering = ['name_en']


class SpecializationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing medical specializations
    """
    queryset = Specialization.objects.filter(is_removed=False)
    serializer_class = SpecializationSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name_en', 'name_ar']
    filterset_fields = ['is_active']
    ordering_fields = ['name_en', 'created']
    ordering = ['name_en']


class StaffViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing staff members
    """
    queryset = Staff.objects.filter(is_removed=False).select_related('role', 'user')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = StaffFilter
    search_fields = [
        'staff_id', 'first_name_en', 'last_name_en', 'first_name_ar', 
        'last_name_ar', 'email', 'national_id'
    ]
    ordering_fields = ['first_name_en', 'last_name_en', 'joining_date', 'created']
    ordering = ['first_name_en', 'last_name_en']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StaffCreateSerializer
        elif self.action == 'list':
            return StaffListSerializer
        return StaffSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        elif self.action in ['retrieve']:
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced search for staff members
        """
        serializer = StaffSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data.get('query', '')
        role = serializer.validated_data.get('role', '')
        employment_status = serializer.validated_data.get('employment_status', '')
        specialization = serializer.validated_data.get('specialization', '')
        is_available = serializer.validated_data.get('is_available')
        language = serializer.validated_data.get('language', 'en')
        
        queryset = self.get_queryset()
        
        # Apply filters
        if query:
            queryset = queryset.filter(
                Q(first_name_en__icontains=query) |
                Q(last_name_en__icontains=query) |
                Q(first_name_ar__icontains=query) |
                Q(last_name_ar__icontains=query) |
                Q(email__icontains=query) |
                Q(staff_id__icontains=query)
            )
        
        if role:
            queryset = queryset.filter(role__code=role)
        
        if employment_status:
            queryset = queryset.filter(employment_status=employment_status)
        
        if specialization:
            queryset = queryset.filter(
                doctor_profile__specializations__name_en__icontains=specialization
            )
        
        if is_available is not None:
            queryset = queryset.filter(doctor_profile__is_available=is_available)
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = StaffListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = StaffListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get staff statistics
        """
        queryset = self.get_queryset()
        
        # Basic counts
        total_staff = queryset.count()
        active_staff = queryset.filter(employment_status='active').count()
        
        # Count by role
        by_role = queryset.values('role__name_en').annotate(count=Count('id')).order_by('-count')
        by_role_dict = {item['role__name_en']: item['count'] for item in by_role}
        
        # Count by status
        by_status = queryset.values('employment_status').annotate(count=Count('id')).order_by('-count')
        by_status_dict = {item['employment_status']: item['count'] for item in by_status}
        
        # Count by specialization (for doctors)
        by_specialization = Doctor.objects.filter(
            staff__in=queryset,
            specializations__isnull=False
        ).values('specializations__name_en').annotate(count=Count('id')).order_by('-count')
        by_specialization_dict = {item['specializations__name_en']: item['count'] for item in by_specialization}
        
        # Specific role counts
        doctors = queryset.filter(role__code__in=['DOC', 'DOCTOR']).count()
        nurses = queryset.filter(role__code='NURSE').count()
        receptionists = queryset.filter(role__code='RECEPTIONIST').count()
        
        stats_data = {
            'total_staff': total_staff,
            'active_staff': active_staff,
            'doctors': doctors,
            'nurses': nurses,
            'receptionists': receptionists,
            'by_role': by_role_dict,
            'by_status': by_status_dict,
            'by_specialization': by_specialization_dict
        }
        
        serializer = StaffStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def schedules(self, request, pk=None):
        """
        Get schedules for a specific staff member
        """
        staff = self.get_object()
        schedules = staff.schedules.filter(is_removed=False)
        serializer = ScheduleSerializer(schedules, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def audit_logs(self, request, pk=None):
        """
        Get audit logs for a specific staff member
        """
        staff = self.get_object()
        logs = staff.audit_logs.all()[:50]  # Limit to last 50 entries
        serializer = StaffAuditLogSerializer(logs, many=True, context={'request': request})
        return Response(serializer.data)


class DoctorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing doctors
    """
    queryset = Doctor.objects.filter(is_removed=False).select_related('staff').prefetch_related('specializations')
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DoctorFilter
    search_fields = [
        'staff__first_name_en', 'staff__last_name_en', 'staff__first_name_ar', 
        'staff__last_name_ar', 'medical_license_number', 'professional_title_en'
    ]
    ordering_fields = ['staff__first_name_en', 'years_of_experience', 'created']
    ordering = ['staff__first_name_en']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get available doctors
        """
        queryset = self.get_queryset().filter(is_available=True, is_accepting_new_patients=True)
        
        # Filter by specialization if provided
        specialization = request.query_params.get('specialization')
        if specialization:
            queryset = queryset.filter(specializations__name_en__icontains=specialization)
        
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Check doctor availability for a specific date/time
        """
        doctor = self.get_object()
        date_str = request.query_params.get('date')
        time_str = request.query_params.get('time')
        
        if not date_str or not time_str:
            return Response(
                {'error': 'Date and time parameters are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            check_time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return Response(
                {'error': 'Invalid date or time format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if doctor is available on this day and time
        day_of_week = check_date.weekday()
        is_available = doctor.schedules.filter(
            day_of_week=day_of_week,
            start_time__lte=check_time,
            end_time__gte=check_time,
            is_active=True
        ).exists()
        
        return Response({
            'doctor': doctor.staff.full_name_en,
            'date': date_str,
            'time': time_str,
            'is_available': is_available
        })


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing staff schedules
    """
    queryset = Schedule.objects.filter(is_removed=False).select_related('staff')
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ScheduleFilter
    search_fields = ['staff__first_name_en', 'staff__last_name_en']
    ordering_fields = ['staff', 'day_of_week', 'start_time']
    ordering = ['staff', 'day_of_week', 'start_time']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsStaffOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def weekly(self, request):
        """
        Get weekly schedule for all staff or specific staff
        """
        staff_id = request.query_params.get('staff_id')
        queryset = self.get_queryset()
        
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        
        # Group by day of week
        weekly_schedule = {}
        for day in range(7):
            day_schedules = queryset.filter(day_of_week=day, is_active=True)
            weekly_schedule[day] = ScheduleSerializer(day_schedules, many=True, context={'request': request}).data
        
        return Response(weekly_schedule)


class CompensationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing staff compensation
    """
    queryset = Compensation.objects.filter(is_removed=False).select_related('staff')
    serializer_class = CompensationSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['staff__first_name_en', 'staff__last_name_en']
    ordering_fields = ['staff', 'effective_from']
    ordering = ['staff', '-effective_from']


class StaffAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing staff audit logs
    """
    queryset = StaffAuditLog.objects.all().select_related('staff', 'changed_by')
    serializer_class = StaffAuditLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['staff__first_name_en', 'staff__last_name_en', 'field_name']
    filterset_fields = ['action', 'changed_by']
    ordering_fields = ['created']
    ordering = ['-created']

