"""
URL configuration for pharmacy project.
"""
from django.urls import path, include

urlpatterns = [
    path('medicine/', include('apps.medicine.urls')),
    path('stock/', include('apps.stock.urls')),
    path('purchase/', include('apps.purchase.urls')),
    path('prescription/', include('apps.prescription.urls')),
]
