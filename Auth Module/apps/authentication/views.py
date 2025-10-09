"""
Authentication views.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, PasswordChangeSerializer, EmailVerificationSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    RoleSerializer, PermissionSerializer, UserRoleSerializer
)
from apps.accounts.models import User, EmailVerificationToken, PasswordResetToken
from apps.authorization.models import Role, Permission, UserRole
from apps.audit.models import AuditLog


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint."""
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create a new user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create email verification token
        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
        
        # Send verification email
        self.send_verification_email(user, token.token)
        
        return Response({
            'message': 'User registered successfully. Please check your email for verification.',
            'user_id': str(user.id)
        }, status=status.HTTP_201_CREATED)
    
    def send_verification_email(self, user, token):
        """Send email verification email."""
        subject = 'Verify your email address'
        message = render_to_string('emails/verify_email.html', {
            'user': user,
            'token': token,
            'verification_url': f"{settings.FRONTEND_URL}/verify-email?token={token}"
        })
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )


class UserLoginView(TokenObtainPairView):
    """User login endpoint."""
    
    serializer_class = UserLoginSerializer
    
    def post(self, request, *args, **kwargs):
        """Handle user login."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        # Create user session
        from apps.accounts.models import UserSession
        session = UserSession.objects.create(
            user=user,
            session_key=request.session.session_key or '',
            refresh_token=str(refresh),
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data,
            'session_id': str(session.id)
        })
    
    def get_client_ip(self, request):
        """Get the client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserLogoutView(generics.GenericAPIView):
    """User logout endpoint."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Handle user logout."""
        # Get refresh token from request
        refresh_token = request.data.get('refresh_token')
        
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        
        # Deactivate user sessions
        from apps.accounts.models import UserSession
        UserSession.objects.filter(
            user=request.user,
            refresh_token=refresh_token
        ).update(is_active=False)
        
        # Log logout event
        AuditLog.log_event(
            event_type='user_logout',
            user=request.user,
            description=f'User logged out: {request.user.email}',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_key=request.session.session_key or '',
        )
        
        return Response({'message': 'Logged out successfully'})
    
    def get_client_ip(self, request):
        """Get the client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get the current user."""
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """User profile update endpoint."""
    
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get the current user."""
        return self.request.user


class PasswordChangeView(generics.GenericAPIView):
    """Password change endpoint."""
    
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Handle password change."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'message': 'Password changed successfully'})


class EmailVerificationView(generics.GenericAPIView):
    """Email verification endpoint."""
    
    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Handle email verification."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'message': 'Email verified successfully'})


class PasswordResetRequestView(generics.GenericAPIView):
    """Password reset request endpoint."""
    
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Handle password reset request."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        
        # Send password reset email
        self.send_reset_email(token.user, token.token)
        
        return Response({'message': 'Password reset email sent'})
    
    def send_reset_email(self, user, token):
        """Send password reset email."""
        subject = 'Reset your password'
        message = render_to_string('emails/password_reset.html', {
            'user': user,
            'token': token,
            'reset_url': f"{settings.FRONTEND_URL}/reset-password?token={token}"
        })
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """Password reset confirmation endpoint."""
    
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Handle password reset confirmation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'message': 'Password reset successfully'})


class RoleListView(generics.ListAPIView):
    """List available roles."""
    
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get roles available to the user."""
        return Role.objects.filter(is_active=True)


class PermissionListView(generics.ListAPIView):
    """List available permissions."""
    
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get permissions available to the user."""
        return Permission.objects.filter(is_active=True)


class UserRoleListView(generics.ListCreateAPIView):
    """List and create user role assignments."""
    
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's role assignments."""
        return UserRole.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        """Create user role assignment."""
        serializer.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_permissions(request):
    """Get user's permissions."""
    user = request.user
    
    # Get permissions from roles
    role_permissions = Permission.objects.filter(
        role_permissions__role__user_roles__user=user,
        role_permissions__role__user_roles__is_active=True,
        is_active=True
    ).distinct()
    
    # Get direct permissions
    direct_permissions = Permission.objects.filter(
        user_permissions__user=user,
        user_permissions__is_active=True,
        is_active=True
    ).distinct()
    
    # Combine permissions
    all_permissions = (role_permissions | direct_permissions).distinct()
    
    return Response({
        'permissions': PermissionSerializer(all_permissions, many=True).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_permission(request):
    """Check if user has a specific permission."""
    permission_name = request.data.get('permission')
    
    if not permission_name:
        return Response({'error': 'Permission name required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user has permission
    has_permission = request.user.has_perm(permission_name)
    
    return Response({
        'permission': permission_name,
        'has_permission': has_permission
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })