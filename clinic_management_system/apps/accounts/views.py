"""
Accounts views.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import User, UserSession, EmailVerificationToken, PasswordResetToken
from .serializers import UserSerializer


class UserListView(generics.ListAPIView):
    """List all users (admin only)."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def get_queryset(self):
        """Get all users."""
        return User.objects.all()


class UserDetailView(generics.RetrieveAPIView):
    """Get user details."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get the current user."""
        return self.request.user


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_sessions(request):
    """Get user's active sessions."""
    sessions = UserSession.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-created_at')
    
    return Response({
        'sessions': [
            {
                'id': str(session.id),
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'created_at': session.created_at,
                'last_activity': session.last_activity,
                'expires_at': session.expires_at
            }
            for session in sessions
        ]
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def terminate_session(request):
    """Terminate a specific session."""
    session_id = request.data.get('session_id')
    
    if not session_id:
        return Response(
            {'error': 'Session ID required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        session = UserSession.objects.get(
            id=session_id,
            user=request.user
        )
        session.is_active = False
        session.save()
        
        return Response({'message': 'Session terminated successfully'})
    except UserSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def terminate_all_sessions(request):
    """Terminate all user sessions except current one."""
    current_session_id = request.data.get('current_session_id')
    
    sessions = UserSession.objects.filter(
        user=request.user,
        is_active=True
    )
    
    if current_session_id:
        sessions = sessions.exclude(id=current_session_id)
    
    sessions.update(is_active=False)
    
    return Response({'message': 'All other sessions terminated successfully'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def account_status(request):
    """Get account status information."""
    user = request.user
    
    return Response({
        'is_verified': user.is_verified,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
        'email_verification_required': not user.is_verified,
    })

