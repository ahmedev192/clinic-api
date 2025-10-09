"""
Authentication URL patterns.
"""
from django.urls import path
from . import views

urlpatterns = [
    # User authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='user-profile-update'),
    
    # Password management
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Email verification
    path('verify-email/', views.EmailVerificationView.as_view(), name='verify-email'),
    
    # Roles and permissions
    path('roles/', views.RoleListView.as_view(), name='role-list'),
    path('permissions/', views.PermissionListView.as_view(), name='permission-list'),
    path('user-roles/', views.UserRoleListView.as_view(), name='user-role-list'),
    path('user-permissions/', views.user_permissions, name='user-permissions'),
    path('check-permission/', views.check_permission, name='check-permission'),
    
    # Health check
    path('health/', views.health_check, name='health-check'),
]
