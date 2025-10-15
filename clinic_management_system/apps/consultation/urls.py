"""
URL configuration for the Consultation & Clinical Notes Module.
Provides comprehensive API endpoints with proper routing.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConsultationViewSet, DiagnosisViewSet, PrescriptionViewSet,
    LabOrderViewSet, AttachmentViewSet, FollowUpNoteViewSet, AuditLogViewSet
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'consultations', ConsultationViewSet, basename='consultation')
router.register(r'diagnoses', DiagnosisViewSet, basename='diagnosis')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')
router.register(r'lab-orders', LabOrderViewSet, basename='laborder')
router.register(r'attachments', AttachmentViewSet, basename='attachment')
router.register(r'follow-up-notes', FollowUpNoteViewSet, basename='followupnote')
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')

# URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional custom endpoints can be added here
    # Example:
    # path('consultations/<uuid:consultation_id>/export/', export_consultation, name='export-consultation'),
]
