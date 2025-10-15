"""
URL configuration for refunds app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.billing.views import RefundViewSet

router = DefaultRouter()
router.register(r'refunds', RefundViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
