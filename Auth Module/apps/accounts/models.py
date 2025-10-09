"""
Account models for user management.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(
        max_length=17,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    last_password_change = models.DateTimeField(default=timezone.now)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # SSO related fields
    external_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    provider = models.CharField(max_length=50, blank=True, null=True)
    provider_data = models.JSONField(default=dict, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['external_id', 'provider']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_locked(self):
        """Check if the user account is locked."""
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False
    
    def lock_account(self, duration_minutes=15):
        """Lock the user account for a specified duration."""
        self.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['locked_until'])
    
    def unlock_account(self):
        """Unlock the user account."""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['locked_until', 'failed_login_attempts'])
    
    def increment_failed_login(self):
        """Increment failed login attempts."""
        self.failed_login_attempts += 1
        self.save(update_fields=['failed_login_attempts'])
    
    def reset_failed_login(self):
        """Reset failed login attempts."""
        self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts'])
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])


class UserProfile(models.Model):
    """
    Extended user profile information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, max_length=500)
    company = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer_not_to_say', 'Prefer not to say'),
        ],
        blank=True
    )
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email} Profile"


class EmailVerificationToken(models.Model):
    """
    Token for email verification.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'email_verification_token'
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_used']),
        ]
    
    def __str__(self):
        return f"Email verification for {self.user.email}"
    
    def is_expired(self):
        """Check if the token is expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if the token is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired()


class PasswordResetToken(models.Model):
    """
    Token for password reset.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'password_reset_token'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_used']),
        ]
    
    def __str__(self):
        return f"Password reset for {self.user.email}"
    
    def is_expired(self):
        """Check if the token is expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if the token is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired()


class UserSession(models.Model):
    """
    User session tracking for security and audit purposes.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    refresh_token = models.CharField(max_length=255, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'user_session'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['refresh_token']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Session for {self.user.email}"
    
    def is_expired(self):
        """Check if the session is expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if the session is valid (active and not expired)."""
        return self.is_active and not self.is_expired()
    
    def deactivate(self):
        """Deactivate the session."""
        self.is_active = False
        self.save(update_fields=['is_active'])

