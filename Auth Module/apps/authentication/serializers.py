"""
Authentication serializers.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from apps.accounts.models import User, UserProfile, EmailVerificationToken, PasswordResetToken
from apps.authorization.models import Role, Permission, UserRole, UserPermission
from apps.audit.models import AuditLog, SecurityEvent


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone_number',
            'password', 'password_confirm', 'timezone', 'language'
        ]
    
    def validate(self, attrs):
        """Validate the registration data."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        return attrs
    
    def create(self, validated_data):
        """Create a new user."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Log registration event
        AuditLog.log_event(
            event_type='user_register',
            user=user,
            description=f'User registered: {user.email}',
            ip_address=self.context.get('request').META.get('REMOTE_ADDR'),
            user_agent=self.context.get('request').META.get('HTTP_USER_AGENT', ''),
            session_key=self.context.get('request').session.session_key or '',
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate login credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            
            if not user:
                # Log failed login attempt
                AuditLog.log_event(
                    event_type='user_login',
                    description=f'Failed login attempt for email: {email}',
                    success=False,
                    error_message='Invalid credentials',
                    severity='medium',
                    ip_address=self.context.get('request').META.get('REMOTE_ADDR'),
                    user_agent=self.context.get('request').META.get('HTTP_USER_AGENT', ''),
                    session_key=self.context.get('request').session.session_key or '',
                )
                
                # Create security event for failed login
                SecurityEvent.objects.create(
                    event_type='failed_login',
                    description=f'Failed login attempt for email: {email}',
                    severity='medium',
                    ip_address=self.context.get('request').META.get('REMOTE_ADDR'),
                    user_agent=self.context.get('request').META.get('HTTP_USER_AGENT', ''),
                    session_key=self.context.get('request').session.session_key or '',
                    risk_score=30,
                )
                
                raise serializers.ValidationError('Invalid credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            if user.is_locked:
                raise serializers.ValidationError('User account is locked.')
            
            # Reset failed login attempts on successful login
            user.reset_failed_login()
            user.update_last_login()
            
            # Log successful login
            AuditLog.log_event(
                event_type='user_login',
                user=user,
                description=f'User logged in: {user.email}',
                ip_address=self.context.get('request').META.get('REMOTE_ADDR'),
                user_agent=self.context.get('request').META.get('HTTP_USER_AGENT', ''),
                session_key=self.context.get('request').session.session_key or '',
            )
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError('Must include email and password.')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'is_verified', 'timezone', 'language', 'avatar', 'profile',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'date_joined', 'last_login']
    
    def get_profile(self, obj):
        """Get user profile data."""
        try:
            profile = obj.profile
            return {
                'bio': profile.bio,
                'company': profile.company,
                'job_title': profile.job_title,
                'website': profile.website,
                'location': profile.location,
                'birth_date': profile.birth_date,
                'gender': profile.gender,
                'preferences': profile.preferences,
            }
        except UserProfile.DoesNotExist:
            return None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    profile = serializers.DictField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number',
            'timezone', 'language', 'avatar', 'profile'
        ]
    
    def update(self, instance, validated_data):
        """Update user and profile."""
        profile_data = validated_data.pop('profile', {})
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile
        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        # Log profile update
        AuditLog.log_event(
            event_type='user_profile_update',
            user=instance,
            description=f'User profile updated: {instance.email}',
            ip_address=self.context.get('request').META.get('REMOTE_ADDR'),
            user_agent=self.context.get('request').META.get('HTTP_USER_AGENT', ''),
            session_key=self.context.get('request').session.session_key or '',
        )
        
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        """Validate current password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
    
    def validate(self, attrs):
        """Validate password change data."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        
        if attrs['current_password'] == attrs['new_password']:
            raise serializers.ValidationError("New password must be different from current password.")
        
        return attrs
    
    def save(self):
        """Change the user's password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.last_password_change = timezone.now()
        user.save()
        
        # Log password change
        AuditLog.log_event(
            event_type='user_password_change',
            user=user,
            description=f'Password changed for user: {user.email}',
            ip_address=self.context.get('request').META.get('REMOTE_ADDR'),
            user_agent=self.context.get('request').META.get('HTTP_USER_AGENT', ''),
            session_key=self.context.get('request').session.session_key or '',
        )


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""
    
    token = serializers.UUIDField()
    
    def validate_token(self, value):
        """Validate verification token."""
        try:
            token_obj = EmailVerificationToken.objects.get(token=value)
            if token_obj.is_used:
                raise serializers.ValidationError('Token has already been used.')
            if token_obj.is_expired():
                raise serializers.ValidationError('Token has expired.')
            return token_obj
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError('Invalid token.')
    
    def save(self):
        """Verify the user's email."""
        token_obj = self.validated_data['token']
        user = token_obj.user
        
        user.is_verified = True
        user.save()
        
        token_obj.is_used = True
        token_obj.save()
        
        # Log email verification
        AuditLog.log_event(
            event_type='user_verify_email',
            user=user,
            description=f'Email verified for user: {user.email}',
            ip_address=self.context.get('request').META.get('REMOTE_ADDR'),
            user_agent=self.context.get('request').META.get('HTTP_USER_AGENT', ''),
            session_key=self.context.get('request').session.session_key or '',
        )


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate email exists."""
        try:
            user = User.objects.get(email=value)
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist.')
    
    def save(self):
        """Create password reset token."""
        user = self.validated_data['email']
        
        # Invalidate existing tokens
        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new token
        token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + timezone.timedelta(hours=1)
        )
        
        # Log password reset request
        AuditLog.log_event(
            event_type='user_password_reset',
            user=user,
            description=f'Password reset requested for user: {user.email}',
            ip_address=self.context.get('request').META.get('REMOTE_ADDR'),
            user_agent=self.context.get('request').META.get('HTTP_USER_AGENT', ''),
            session_key=self.context.get('request').session.session_key or '',
        )
        
        return token


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.UUIDField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate_token(self, value):
        """Validate reset token."""
        try:
            token_obj = PasswordResetToken.objects.get(token=value)
            if token_obj.is_used:
                raise serializers.ValidationError('Token has already been used.')
            if token_obj.is_expired():
                raise serializers.ValidationError('Token has expired.')
            return token_obj
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError('Invalid token.')
    
    def validate(self, attrs):
        """Validate password reset data."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def save(self):
        """Reset the user's password."""
        token_obj = self.validated_data['token']
        user = token_obj.user
        
        user.set_password(self.validated_data['new_password'])
        user.last_password_change = timezone.now()
        user.reset_failed_login()
        user.save()
        
        token_obj.is_used = True
        token_obj.save()
        
        # Log password reset
        AuditLog.log_event(
            event_type='user_password_reset',
            user=user,
            description=f'Password reset completed for user: {user.email}',
            ip_address=self.context.get('request').META.get('REMOTE_ADDR'),
            user_agent=self.context.get('request').META.get('HTTP_USER_AGENT', ''),
            session_key=self.context.get('request').session.session_key or '',
        )


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for roles."""
    
    user_count = serializers.SerializerMethodField()
    permission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'display_name', 'description', 'is_active',
            'is_system', 'user_count', 'permission_count', 'created_at'
        ]
        read_only_fields = ['id', 'is_system', 'created_at']
    
    def get_user_count(self, obj):
        """Get number of users with this role."""
        return obj.user_roles.filter(is_active=True).count()
    
    def get_permission_count(self, obj):
        """Get number of permissions for this role."""
        return obj.role_permissions.count()


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for permissions."""
    
    class Meta:
        model = Permission
        fields = [
            'id', 'name', 'display_name', 'description', 'resource',
            'action', 'is_active', 'is_system', 'created_at'
        ]
        read_only_fields = ['id', 'is_system', 'created_at']


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for user role assignments."""
    
    role = RoleSerializer(read_only=True)
    role_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'role', 'role_id', 'assigned_at', 'expires_at',
            'is_active', 'is_expired'
        ]
        read_only_fields = ['id', 'assigned_at']
    
    def create(self, validated_data):
        """Create user role assignment."""
        role_id = validated_data.pop('role_id')
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise serializers.ValidationError('Invalid role ID.')
        
        user = self.context['request'].user
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={
                'assigned_by': user,
                'is_active': True
            }
        )
        
        if not created:
            raise serializers.ValidationError('User already has this role.')
        
        # Log role assignment
        AuditLog.log_event(
            event_type='role_assign',
            user=user,
            description=f'Role assigned: {role.display_name}',
            content_object=user_role,
            ip_address=self.context.get('request').META.get('REMOTE_ADDR'),
            user_agent=self.context.get('request').META.get('HTTP_USER_AGENT', ''),
            session_key=self.context.get('request').session.session_key or '',
        )
        
        return user_role

