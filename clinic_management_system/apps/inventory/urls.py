"""
Inventory URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, SupplierViewSet, ItemViewSet, StockMovementViewSet,
    PurchaseOrderViewSet, MaintenanceRecordViewSet, AlertViewSet,
    ItemIntegrationViewSet, StockMovementIntegrationViewSet
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'suppliers', SupplierViewSet, basename='suppliers')
router.register(r'items', ItemViewSet, basename='items')
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movements')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-orders')
router.register(r'maintenance-records', MaintenanceRecordViewSet, basename='maintenance-records')
router.register(r'alerts', AlertViewSet, basename='alerts')

# Integration APIs
router.register(r'integration/items', ItemIntegrationViewSet, basename='integration-items')
router.register(r'integration/stock-movements', StockMovementIntegrationViewSet, basename='integration-stock-movements')

urlpatterns = [
    path('', include(router.urls)),
]
