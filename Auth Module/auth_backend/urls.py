"""
URL configuration for auth_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.authentication.views import health_check

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Health check
    path('api/health/', health_check, name='health-check'),
    
    # Authentication endpoints
    path('api/v1/auth/', include('apps.authentication.urls')),
    
    # Account management
    path('api/v1/accounts/', include('apps.accounts.urls')),
    
    # Authorization endpoints
    path('api/v1/authorization/', include('apps.authorization.urls')),
    
    # OAuth2/OIDC endpoints
    path('api/v1/oauth2/', include('apps.oauth2.urls')),
    
    # OAuth2 Provider endpoints
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    
    # Django Allauth
    path('accounts/', include('allauth.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
