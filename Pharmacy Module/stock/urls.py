from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockViewSet, StockAlertViewSet, StockTransactionViewSet

router = DefaultRouter()
router.register(r'stock', StockViewSet)
router.register(r'alerts', StockAlertViewSet)
router.register(r'transactions', StockTransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
