"""
URL configuration for billing app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet, DoctorViewSet, ServiceCategoryViewSet, ServiceViewSet,
    InvoiceViewSet, InvoiceItemViewSet, PaymentMethodViewSet, PaymentViewSet,
    RefundViewSet, DiscountViewSet, AuditLogViewSet, FinancialReportsViewSet
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'service-categories', ServiceCategoryViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'invoice-items', InvoiceItemViewSet)
router.register(r'payment-methods', PaymentMethodViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'refunds', RefundViewSet)
router.register(r'discounts', DiscountViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'reports', FinancialReportsViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]
