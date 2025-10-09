"""
URL configuration for the appointments app.

Defines all API endpoints for the Appointments & Scheduling module.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')
router.register(r'doctor-availability', views.DoctorAvailabilityViewSet, basename='doctor-availability')
router.register(r'waiting-list', views.WaitingListViewSet, basename='waiting-list')
router.register(r'reminders', views.ReminderViewSet, basename='reminder')
router.register(r'doctors', views.DoctorViewSet, basename='doctor')
router.register(r'patients', views.PatientViewSet, basename='patient')
router.register(r'clinic-settings', views.ClinicSettingsViewSet, basename='clinic-settings')

app_name = 'appointments'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional endpoints
    path('appointments/<uuid:appointment_id>/audit-log/', 
         views.appointment_audit_log, name='appointment-audit-log'),
    path('health/', views.health_check, name='health-check'),
]
