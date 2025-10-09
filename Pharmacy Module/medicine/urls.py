from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MedicineViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'medicines', MedicineViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
