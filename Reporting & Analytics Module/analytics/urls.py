"""
URL configuration for analytics app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportTemplateViewSet, ReportQueryViewSet, ReportResultViewSet,
    DataSourceViewSet, ReportScheduleViewSet, FinancialReportViewSet,
    DemographicReportViewSet, DoctorPerformanceViewSet, AppointmentStatsViewSet,
    CustomReportViewSet, ExportViewSet
)

# Create router
router = DefaultRouter()
router.register(r'templates', ReportTemplateViewSet)
router.register(r'queries', ReportQueryViewSet)
router.register(r'results', ReportResultViewSet)
router.register(r'data-sources', DataSourceViewSet)
router.register(r'schedules', ReportScheduleViewSet)
router.register(r'financial', FinancialReportViewSet, basename='financial')
router.register(r'demographic', DemographicReportViewSet, basename='demographic')
router.register(r'doctor-performance', DoctorPerformanceViewSet, basename='doctor-performance')
router.register(r'appointment-stats', AppointmentStatsViewSet, basename='appointment-stats')
router.register(r'custom', CustomReportViewSet, basename='custom')
router.register(r'export', ExportViewSet, basename='export')

urlpatterns = [
    path('', include(router.urls)),
]
