"""
URL configuration for clinic_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 endpoints
    path('api/v1/', include([
        # Authentication & Authorization
        path('auth/', include('apps.authentication.urls')),
        path('oauth2/', include('apps.oauth2.urls')),
        path('accounts/', include('apps.accounts.urls')),
        
        # Core Business Modules
        path('patients/', include('apps.patient_management.urls')),
        path('staff/', include('apps.staff_management.urls')),
        path('appointments/', include('apps.appointments.urls')),
        path('consultations/', include('apps.consultation.urls')),
        
        # Laboratory modules
        path('lab-tests/', include('apps.lab_tests.urls')),
        path('lab-requests/', include('apps.lab_requests.urls')),
        path('lab-samples/', include('apps.lab_samples.urls')),
        path('lab-results/', include('apps.lab_results.urls')),
        path('lab-reports/', include('apps.lab_reports.urls')),
        path('laboratory/', include('apps.laboratory_management.urls')),
        
        # Pharmacy modules
        path('medicine/', include('apps.medicine.urls')),
        path('pharmacy/', include('apps.pharmacy.urls')),
        path('prescriptions/', include('apps.prescription.urls')),
        path('purchases/', include('apps.purchase.urls')),
        path('stock/', include('apps.stock.urls')),
        
        # Inventory and billing
        path('inventory/', include('apps.inventory.urls')),
        path('billing/', include('apps.billing.urls')),
        path('discounts/', include('apps.discounts.urls')),
        path('invoices/', include('apps.invoices.urls')),
        path('payments/', include('apps.payments.urls')),
        path('refunds/', include('apps.refunds.urls')),
        
        # Analytics and reporting
        path('analytics/', include('apps.analytics.urls')),
        path('clinic-analytics/', include('apps.clinic_analytics.urls')),
        
        # Admin and monitoring
        path('dashboard/', include('apps.dashboard.urls')),
        path('notifications/', include('apps.notifications.urls')),
        path('integration/', include('apps.integration.urls')),
        path('monitoring/', include('apps.monitoring.urls')),
        
        # Audit
        path('audit/', include('apps.audit.urls')),
        path('audit-logs/', include('apps.audit_logs.urls')),
    ])),
    
    # Health check
    path('health/', include('apps.monitoring.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
