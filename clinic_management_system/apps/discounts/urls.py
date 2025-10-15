"""
URL configuration for discounts app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.billing.views import DiscountViewSet

router = DefaultRouter()
router.register(r'discounts', DiscountViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
