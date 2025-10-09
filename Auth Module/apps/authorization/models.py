"""
Authorization models for role-based access control.
"""
import uuid
from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from apps.accounts.models import User


class Role(models.Model):
    """
    Role model for grouping permissions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    display_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)  # System roles cannot be deleted
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_roles'
    )
    
    class Meta:
        db_table = 'auth_role'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.display_name


class Permission(models.Model):
    """
    Custom permission model for fine-grained access control.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    display_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    resource = models.CharField(max_length=100, db_index=True)  # e.g., 'user', 'role', 'audit'
    action = models.CharField(max_length=50, db_index=True)  # e.g., 'create', 'read', 'update', 'delete'
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)  # System permissions cannot be deleted
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_permissions'
    )
    
    class Meta:
        db_table = 'auth_permission'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        unique_together = ['resource', 'action']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['resource', 'action']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.resource}.{self.action}"
    
    @property
    def codename(self):
        """Return the permission codename."""
        return f"{self.resource}.{self.action}"


class UserRole(models.Model):
    """
    Many-to-many relationship between User and Role.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_user_roles'
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'auth_user_role'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        unique_together = ['user', 'role']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.role.display_name}"
    
    def is_expired(self):
        """Check if the role assignment is expired."""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
    
    def is_valid(self):
        """Check if the role assignment is valid (active and not expired)."""
        return self.is_active and not self.is_expired()


class RolePermission(models.Model):
    """
    Many-to-many relationship between Role and Permission.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_role_permissions'
    )
    
    class Meta:
        db_table = 'auth_role_permission'
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
        unique_together = ['role', 'permission']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['permission']),
        ]
    
    def __str__(self):
        return f"{self.role.display_name} - {self.permission.display_name}"


class UserPermission(models.Model):
    """
    Direct permission assignment to users (bypassing roles).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='user_permissions')
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_user_permissions'
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'auth_user_permission'
        verbose_name = 'User Permission'
        verbose_name_plural = 'User Permissions'
        unique_together = ['user', 'permission']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['permission', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.permission.display_name}"
    
    def is_expired(self):
        """Check if the permission assignment is expired."""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
    
    def is_valid(self):
        """Check if the permission assignment is valid (active and not expired)."""
        return self.is_active and not self.is_expired()


class Resource(models.Model):
    """
    Resource model for defining what can be accessed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    display_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    resource_type = models.CharField(
        max_length=50,
        choices=[
            ('model', 'Model'),
            ('api', 'API Endpoint'),
            ('feature', 'Feature'),
            ('page', 'Page'),
        ]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_resource'
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.display_name


class Action(models.Model):
    """
    Action model for defining what can be done.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, db_index=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_action'
        verbose_name = 'Action'
        verbose_name_plural = 'Actions'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.display_name

