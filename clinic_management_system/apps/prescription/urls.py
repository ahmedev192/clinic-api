from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrescriptionViewSet, PrescriptionItemViewSet, DispensingRecordViewSet

router = DefaultRouter()
router.register(r'prescriptions', PrescriptionViewSet)
router.register(r'prescription-items', PrescriptionItemViewSet)
router.register(r'dispensing-records', DispensingRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
