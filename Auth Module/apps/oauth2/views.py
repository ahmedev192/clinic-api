"""
OAuth2/OIDC views.
"""
import secrets
import hashlib
import base64
import requests
import json
from urllib.parse import urlencode, parse_qs
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import OAuth2Provider, OAuth2Session, ExternalAccount, OAuth2Token, OAuth2AuditLog
from .serializers import (
    OAuth2ProviderSerializer, OAuth2ProviderDetailSerializer,
    OAuth2SessionSerializer, ExternalAccountSerializer, OAuth2TokenSerializer,
    OAuth2AuthorizeSerializer, OAuth2CallbackSerializer,
    AccountLinkingSerializer, AccountUnlinkingSerializer
)
from apps.audit.models import AuditLog
from apps.authorization.models import Role

User = get_user_model()


class OAuth2ProviderListView(generics.ListAPIView):
    """List available OAuth2 providers."""
    
    serializer_class = OAuth2ProviderSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get active OAuth2 providers."""
        return OAuth2Provider.objects.filter(is_active=True)


class OAuth2ProviderDetailView(generics.RetrieveAPIView):
    """Get OAuth2 provider details (admin only)."""
    
    serializer_class = OAuth2ProviderDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Get all OAuth2 providers."""
        return OAuth2Provider.objects.all()


class OAuth2AuthorizeView(generics.GenericAPIView):
    """OAuth2 authorization endpoint."""
    
    serializer_class = OAuth2AuthorizeSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Initiate OAuth2 authorization flow."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        provider = serializer.validated_data['provider_id']
        redirect_uri = serializer.validated_data.get('redirect_uri') or provider.redirect_uris[0]
        state = serializer.validated_data.get('state') or self.generate_state()
        nonce = serializer.validated_data.get('nonce') or self.generate_nonce()
        scopes = serializer.validated_data.get('scopes') or provider.scopes
        
        # Generate PKCE parameters
        code_verifier = self.generate_code_verifier()
        code_challenge = self.generate_code_challenge(code_verifier)
        
        # Create OAuth2 session
        session = OAuth2Session.objects.create(
            provider=provider,
            state=state,
            nonce=nonce,
            code_verifier=code_verifier,
            code_challenge=code_challenge,
            code_challenge_method='S256',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        # Generate authorization URL
        auth_url = provider.get_authorization_url(
            state=state,
            nonce=nonce,
            code_challenge=code_challenge,
            code_challenge_method='S256'
        )
        
        # Log authorization request
        OAuth2AuditLog.objects.create(
            provider=provider,
            session=session,
            event_type='authorize',
            success=True,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            request_data={'scopes': scopes, 'redirect_uri': redirect_uri}
        )
        
        return Response({
            'authorization_url': auth_url,
            'state': state,
            'session_id': str(session.id)
        })
    
    def generate_state(self):
        """Generate random state parameter."""
        return secrets.token_urlsafe(32)
    
    def generate_nonce(self):
        """Generate random nonce parameter."""
        return secrets.token_urlsafe(32)
    
    def generate_code_verifier(self):
        """Generate PKCE code verifier."""
        return secrets.token_urlsafe(32)
    
    def generate_code_challenge(self, code_verifier):
        """Generate PKCE code challenge."""
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    
    def get_client_ip(self, request):
        """Get the client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class OAuth2CallbackView(generics.GenericAPIView):
    """OAuth2 callback endpoint."""
    
    serializer_class = OAuth2CallbackSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Handle OAuth2 callback."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        state = serializer.validated_data['state']
        
        # Find OAuth2 session
        try:
            session = OAuth2Session.objects.get(state=state, is_active=True)
        except OAuth2Session.DoesNotExist:
            return Response({'error': 'Invalid state parameter'}, status=status.HTTP_400_BAD_REQUEST)
        
        provider = session.provider
        
        # Exchange code for tokens
        token_data = provider.get_token_data(
            code=code,
            redirect_uri=request.data.get('redirect_uri', provider.redirect_uris[0]),
            code_verifier=session.code_verifier
        )
        
        try:
            # Make token request
            response = requests.post(provider.token_url, data=token_data)
            response.raise_for_status()
            token_response = response.json()
            
            # Update session with tokens
            session.access_token = token_response.get('access_token', '')
            session.refresh_token = token_response.get('refresh_token', '')
            session.id_token = token_response.get('id_token', '')
            session.token_type = token_response.get('token_type', 'Bearer')
            session.scope = token_response.get('scope', '')
            
            # Calculate expiration
            expires_in = token_response.get('expires_in', 3600)
            session.expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)
            session.save()
            
            # Get user info
            user_info = self.get_user_info(provider, session.access_token)
            session.external_user_id = user_info.get('sub', '')
            session.external_username = user_info.get('preferred_username', '')
            session.external_email = user_info.get('email', '')
            session.external_claims = user_info
            session.save()
            
            # Log token exchange
            OAuth2AuditLog.objects.create(
                provider=provider,
                session=session,
                event_type='token_exchange',
                success=True,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                response_data=token_response
            )
            
            # Handle user provisioning or linking
            user = self.handle_user_provisioning(provider, session, user_info)
            
            if user:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                # Create external account if needed
                if not ExternalAccount.objects.filter(
                    user=user,
                    provider=provider,
                    external_user_id=session.external_user_id
                ).exists():
                    ExternalAccount.objects.create(
                        user=user,
                        provider=provider,
                        external_user_id=session.external_user_id,
                        external_username=session.external_username,
                        external_email=session.external_email,
                        external_claims=session.external_claims,
                        is_verified=True
                    )
                
                # Log successful login
                OAuth2AuditLog.objects.create(
                    provider=provider,
                    user=user,
                    session=session,
                    event_type='oauth_login',
                    success=True,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    external_user_id=session.external_user_id,
                    external_claims=session.external_claims
                )
                
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_verified': user.is_verified
                    },
                    'provider': provider.display_name
                })
            else:
                return Response({'error': 'User provisioning failed'}, status=status.HTTP_400_BAD_REQUEST)
        
        except requests.RequestException as e:
            # Log error
            OAuth2AuditLog.objects.create(
                provider=provider,
                session=session,
                event_type='token_exchange',
                success=False,
                error_message=str(e),
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            
            return Response({'error': 'Token exchange failed'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_user_info(self, provider, access_token):
        """Get user information from provider."""
        if not provider.user_info_url:
            return {}
        
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(provider.user_info_url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def handle_user_provisioning(self, provider, session, user_info):
        """Handle user provisioning or linking."""
        email = user_info.get('email')
        if not email:
            return None
        
        # Check if user already exists
        try:
            user = User.objects.get(email=email)
            
            # Check if account is already linked
            if not ExternalAccount.objects.filter(
                user=user,
                provider=provider,
                external_user_id=session.external_user_id
            ).exists():
                # Link existing account
                ExternalAccount.objects.create(
                    user=user,
                    provider=provider,
                    external_user_id=session.external_user_id,
                    external_username=session.external_username,
                    external_email=session.external_email,
                    external_claims=session.external_claims,
                    is_verified=True
                )
            
            return user
        
        except User.DoesNotExist:
            # JIT provisioning
            if not provider.jit_provisioning:
                return None
            
            # Create new user
            user = User.objects.create_user(
                email=email,
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
                is_verified=True,
                external_id=session.external_user_id,
                provider=provider.name,
                provider_data=session.external_claims
            )
            
            # Assign default roles
            for role_name in provider.auto_assign_roles:
                try:
                    role = Role.objects.get(name=role_name, is_active=True)
                    UserRole.objects.create(
                        user=user,
                        role=role,
                        is_active=True
                    )
                except Role.DoesNotExist:
                    pass
            
            # Log JIT provisioning
            OAuth2AuditLog.objects.create(
                provider=provider,
                user=user,
                session=session,
                event_type='jit_provisioning',
                success=True,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                external_user_id=session.external_user_id,
                external_claims=session.external_claims
            )
            
            return user
    
    def get_client_ip(self, request):
        """Get the client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ExternalAccountListView(generics.ListAPIView):
    """List user's external accounts."""
    
    serializer_class = ExternalAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's external accounts."""
        return ExternalAccount.objects.filter(user=self.request.user, is_active=True)


class AccountLinkingView(generics.GenericAPIView):
    """Link external account to user."""
    
    serializer_class = AccountLinkingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Link external account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        provider = serializer.validated_data['provider_id']
        external_user_id = serializer.validated_data['external_user_id']
        external_username = serializer.validated_data.get('external_username', '')
        external_email = serializer.validated_data.get('external_email', '')
        external_claims = serializer.validated_data.get('external_claims', {})
        
        # Create external account
        external_account = ExternalAccount.objects.create(
            user=request.user,
            provider=provider,
            external_user_id=external_user_id,
            external_username=external_username,
            external_email=external_email,
            external_claims=external_claims,
            is_verified=True
        )
        
        # Log account linking
        OAuth2AuditLog.objects.create(
            provider=provider,
            user=request.user,
            event_type='account_linking',
            success=True,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            external_user_id=external_user_id,
            external_claims=external_claims
        )
        
        return Response({
            'message': 'Account linked successfully',
            'external_account': ExternalAccountSerializer(external_account).data
        })
    
    def get_client_ip(self, request):
        """Get the client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AccountUnlinkingView(generics.GenericAPIView):
    """Unlink external account from user."""
    
    serializer_class = AccountUnlinkingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Unlink external account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        external_account = serializer.validated_data['external_account_id']
        
        # Log account unlinking
        OAuth2AuditLog.objects.create(
            provider=external_account.provider,
            user=request.user,
            event_type='account_linking',
            success=True,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            external_user_id=external_account.external_user_id,
            external_claims=external_account.external_claims
        )
        
        # Deactivate external account
        external_account.is_active = False
        external_account.save()
        
        return Response({'message': 'Account unlinked successfully'})
    
    def get_client_ip(self, request):
        """Get the client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def oauth2_sessions(request):
    """Get user's OAuth2 sessions."""
    sessions = OAuth2Session.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('provider')
    
    return Response({
        'sessions': OAuth2SessionSerializer(sessions, many=True).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_oauth2_session(request):
    """Revoke OAuth2 session."""
    session_id = request.data.get('session_id')
    
    if not session_id:
        return Response({'error': 'Session ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        session = OAuth2Session.objects.get(
            id=session_id,
            user=request.user,
            is_active=True
        )
        
        # Deactivate session
        session.deactivate()
        
        # Log session revocation
        OAuth2AuditLog.objects.create(
            provider=session.provider,
            user=request.user,
            session=session,
            event_type='oauth_logout',
            success=True,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        return Response({'message': 'Session revoked successfully'})
    
    except OAuth2Session.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

