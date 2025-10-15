"""
URL configuration for patient_management app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patients', views.PatientViewSet)
router.register(r'medical-history', views.MedicalHistoryViewSet)
router.register(r'allergies', views.AllergyViewSet)
router.register(r'chronic-conditions', views.ChronicConditionViewSet)
router.register(r'documents', views.PatientDocumentViewSet)
router.register(r'search-logs', views.PatientSearchLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
