"""
Audit Logging Views

This module provides API views for accessing audit logs and system events.
"""

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import AuditLog, PatientAccessLog, DataExportLog, SystemEventLog
from .serializers import (
    AuditLogSerializer, PatientAccessLogSerializer, 
    DataExportLogSerializer, SystemEventLogSerializer
)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for audit logs.
    Read-only access to audit trail.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'user', 'content_type', 'timestamp']
    search_fields = ['description', 'field_name', 'old_value', 'new_value']
    ordering_fields = ['timestamp', 'action', 'user']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter audit logs based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-admin users can only see their own audit logs
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get recent activity for the current user"""
        queryset = self.get_queryset().filter(user=request.user)[:50]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """Get audit logs for a specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response({'error': 'patient_id parameter is required'}, status=400)
        
        queryset = self.get_queryset().filter(
            Q(content_type__model='patient', object_id=patient_id) |
            Q(description__icontains=patient_id)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PatientAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for patient access logs.
    Read-only access to patient data access history.
    """
    queryset = PatientAccessLog.objects.all()
    serializer_class = PatientAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'user', 'access_type', 'timestamp']
    search_fields = ['reason', 'request_path']
    ordering_fields = ['timestamp', 'access_type']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter access logs based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-admin users can only see their own access logs
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset


class DataExportLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for data export logs.
    Read-only access to export history.
    """
    queryset = DataExportLog.objects.all()
    serializer_class = DataExportLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'export_type', 'format', 'timestamp']
    search_fields = ['export_type', 'file_path']
    ordering_fields = ['timestamp', 'export_type']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter export logs based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-admin users can only see their own export logs
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset


class SystemEventLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for system event logs.
    Read-only access to system events and errors.
    """
    queryset = SystemEventLog.objects.all()
    serializer_class = SystemEventLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'user', 'module', 'is_resolved', 'timestamp']
    search_fields = ['title', 'description', 'module']
    ordering_fields = ['timestamp', 'event_type', 'is_resolved']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter system events based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-admin users can only see their own events
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark a system event as resolved"""
        event = self.get_object()
        notes = request.data.get('notes', '')
        
        event.resolve(user=request.user, notes=notes)
        
        serializer = self.get_serializer(event)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unresolved(self, request):
        """Get unresolved system events"""
        queryset = self.get_queryset().filter(is_resolved=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
