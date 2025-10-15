"""
URL configuration for audit_logs app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'logs', views.AuditLogViewSet)
router.register(r'patient-access', views.PatientAccessLogViewSet)
router.register(r'exports', views.DataExportLogViewSet)
router.register(r'system-events', views.SystemEventLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
