"""
Tests for authentication views.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from apps.accounts.models import User, EmailVerificationToken, PasswordResetToken
from apps.authorization.models import Role, Permission


class AuthenticationAPITestCase(APITestCase):
    """Test cases for authentication API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
    
    def test_user_registration(self):
        """Test user registration endpoint."""
        url = reverse('user-register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user_id', response.data)
        
        # Check if user was created
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())
    
    def test_user_registration_invalid_data(self):
        """Test user registration with invalid data."""
        url = reverse('user-register')
        invalid_data = {
            'email': 'invalid-email',
            'password': '123',  # Too short
            'password_confirm': '456'  # Doesn't match
        }
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Test user login endpoint."""
        # Create a user first
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name']
        )
        
        url = reverse('user-login')
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials."""
        url = reverse('user-login')
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_logout(self):
        """Test user logout endpoint."""
        # Create and login a user
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        # Get tokens
        url = reverse('user-login')
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Logout
        url = reverse('user-logout')
        logout_data = {'refresh_token': refresh_token}
        response = self.client.post(url, logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_user_profile(self):
        """Test get user profile endpoint."""
        # Create and login a user
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        # Get tokens
        url = reverse('user-login')
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(url, login_data, format='json')
        access_token = login_response.data['access']
        
        # Get profile
        url = reverse('user-profile')
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.get(url, headers=headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])
    
    def test_password_change(self):
        """Test password change endpoint."""
        # Create and login a user
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        # Get tokens
        url = reverse('user-login')
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(url, login_data, format='json')
        access_token = login_response.data['access']
        
        # Change password
        url = reverse('password-change')
        password_data = {
            'current_password': self.user_data['password'],
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.post(url, password_data, format='json', headers=headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_password_reset_request(self):
        """Test password reset request endpoint."""
        # Create a user
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        url = reverse('password-reset-request')
        reset_data = {'email': self.user_data['email']}
        response = self.client.post(url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if reset token was created
        self.assertTrue(PasswordResetToken.objects.filter(user=user).exists())
    
    def test_email_verification(self):
        """Test email verification endpoint."""
        # Create a user
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        # Create verification token
        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
        
        url = reverse('verify-email')
        verify_data = {'token': str(token.token)}
        response = self.client.post(url, verify_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if user is verified
        user.refresh_from_db()
        self.assertTrue(user.is_verified)


class AuthorizationAPITestCase(APITestCase):
    """Test cases for authorization API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create roles and permissions
        self.role = Role.objects.create(
            name='test_role',
            display_name='Test Role',
            description='Test role for testing'
        )
        
        self.permission = Permission.objects.create(
            name='test.permission',
            display_name='Test Permission',
            description='Test permission for testing',
            resource='test',
            action='permission'
        )
    
    def test_get_roles(self):
        """Test get roles endpoint."""
        # Login user
        url = reverse('user-login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        login_response = self.client.post(url, login_data, format='json')
        access_token = login_response.data['access']
        
        # Get roles
        url = reverse('role-list')
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.get(url, headers=headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_get_permissions(self):
        """Test get permissions endpoint."""
        # Login user
        url = reverse('user-login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        login_response = self.client.post(url, login_data, format='json')
        access_token = login_response.data['access']
        
        # Get permissions
        url = reverse('permission-list')
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.get(url, headers=headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_get_user_permissions(self):
        """Test get user permissions endpoint."""
        # Login user
        url = reverse('user-login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        login_response = self.client.post(url, login_data, format='json')
        access_token = login_response.data['access']
        
        # Get user permissions
        url = reverse('user-permissions')
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.get(url, headers=headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('permissions', response.data)
    
    def test_check_permission(self):
        """Test check permission endpoint."""
        # Login user
        url = reverse('user-login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        login_response = self.client.post(url, login_data, format='json')
        access_token = login_response.data['access']
        
        # Check permission
        url = reverse('check-permission')
        permission_data = {'permission': 'test.permission'}
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.post(url, permission_data, format='json', headers=headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('has_permission', response.data)


class OAuth2APITestCase(APITestCase):
    """Test cases for OAuth2 API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        from apps.oauth2.models import OAuth2Provider
        
        self.oauth_provider = OAuth2Provider.objects.create(
            name='test_provider',
            display_name='Test Provider',
            provider_type='generic',
            is_active=True,
            client_id='test_client_id',
            client_secret='test_client_secret',
            authorization_url='https://test.com/auth',
            token_url='https://test.com/token',
            user_info_url='https://test.com/userinfo',
            scopes=['openid', 'profile', 'email'],
            redirect_uris=['http://localhost:3000/callback'],
            jit_provisioning=True
        )
    
    def test_get_oauth2_providers(self):
        """Test get OAuth2 providers endpoint."""
        url = reverse('oauth2-provider-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_oauth2_authorize(self):
        """Test OAuth2 authorization endpoint."""
        url = reverse('oauth2-authorize')
        authorize_data = {
            'provider_id': str(self.oauth_provider.id),
            'redirect_uri': 'http://localhost:3000/callback'
        }
        response = self.client.post(url, authorize_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('authorization_url', response.data)
        self.assertIn('state', response.data)
        self.assertIn('session_id', response.data)

