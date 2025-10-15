"""
URL configuration for staff_management app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoleViewSet, SpecializationViewSet, StaffViewSet, DoctorViewSet,
    ScheduleViewSet, CompensationViewSet, StaffAuditLogViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'specializations', SpecializationViewSet, basename='specialization')
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'compensations', CompensationViewSet, basename='compensation')
router.register(r'audit-logs', StaffAuditLogViewSet, basename='audit-log')

app_name = 'staff_management'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional custom endpoints can be added here
    # Example:
    # path('staff/export/', export_staff_data, name='export-staff'),
    # path('doctors/availability/', check_doctor_availability, name='doctor-availability'),
]
