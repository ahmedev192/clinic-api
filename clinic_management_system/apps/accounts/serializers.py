"""
Accounts serializers.
"""
from rest_framework import serializers
from .models import User, UserSession, EmailVerificationToken, PasswordResetToken


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'is_verified', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_verified', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]


class UserSessionSerializer(serializers.ModelSerializer):
    """User session serializer."""
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'session_key', 'ip_address', 'user_agent',
            'is_active', 'created_at', 'last_activity', 'expires_at'
        ]
        read_only_fields = [
            'id', 'user', 'session_key', 'created_at', 'last_activity'
        ]


class EmailVerificationTokenSerializer(serializers.ModelSerializer):
    """Email verification token serializer."""
    
    class Meta:
        model = EmailVerificationToken
        fields = ['id', 'user', 'token', 'is_used', 'created_at', 'expires_at']
        read_only_fields = ['id', 'user', 'token', 'created_at']


class PasswordResetTokenSerializer(serializers.ModelSerializer):
    """Password reset token serializer."""
    
    class Meta:
        model = PasswordResetToken
        fields = ['id', 'user', 'token', 'is_used', 'created_at', 'expires_at']
        read_only_fields = ['id', 'user', 'token', 'created_at']

