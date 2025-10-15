"""
URL configuration for clinic_analytics project.
"""
from django.urls import path, include

urlpatterns = [
    path('', include('apps.analytics.urls')),
]
