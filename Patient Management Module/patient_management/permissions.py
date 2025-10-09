"""
Patient Management Permissions

This module provides custom permissions for patient management operations.
"""

from rest_framework import permissions
from django.contrib.auth.models import Group


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the snippet.
        return obj.created_by == request.user


class IsPatientOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission for patient records.
    Only the creator or staff can access patient records.
    """
    
    def has_object_permission(self, request, view, obj):
        # Staff can access all patient records
        if request.user.is_staff:
            return True
        
        # Users can only access patients they created
        return obj.created_by == request.user


class CanViewPatientData(permissions.BasePermission):
    """
    Permission to view patient data based on user role.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Staff can view all patient data
        if request.user.is_staff:
            return True
        
        # Check if user is in appropriate groups
        user_groups = request.user.groups.values_list('name', flat=True)
        allowed_groups = ['doctors', 'nurses', 'receptionists', 'administrators']
        
        return any(group in user_groups for group in allowed_groups)
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Staff can view all patient data
        if request.user.is_staff:
            return True
        
        # Users can view patients they created
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        # Check if user is in appropriate groups
        user_groups = request.user.groups.values_list('name', flat=True)
        allowed_groups = ['doctors', 'nurses', 'receptionists', 'administrators']
        
        return any(group in user_groups for group in allowed_groups)


class CanEditPatientData(permissions.BasePermission):
    """
    Permission to edit patient data based on user role.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Staff can edit all patient data
        if request.user.is_staff:
            return True
        
        # Check if user is in appropriate groups
        user_groups = request.user.groups.values_list('name', flat=True)
        allowed_groups = ['doctors', 'nurses', 'receptionists', 'administrators']
        
        return any(group in user_groups for group in allowed_groups)
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Staff can edit all patient data
        if request.user.is_staff:
            return True
        
        # Users can edit patients they created
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        # Check if user is in appropriate groups
        user_groups = request.user.groups.values_list('name', flat=True)
        allowed_groups = ['doctors', 'nurses', 'receptionists', 'administrators']
        
        return any(group in user_groups for group in allowed_groups)


class CanDeletePatientData(permissions.BasePermission):
    """
    Permission to delete patient data based on user role.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only staff and administrators can delete patient data
        if request.user.is_staff:
            return True
        
        # Check if user is in administrator group
        user_groups = request.user.groups.values_list('name', flat=True)
        return 'administrators' in user_groups
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Only staff and administrators can delete patient data
        if request.user.is_staff:
            return True
        
        # Check if user is in administrator group
        user_groups = request.user.groups.values_list('name', flat=True)
        return 'administrators' in user_groups


class CanAccessMedicalHistory(permissions.BasePermission):
    """
    Permission to access medical history data.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Staff can access all medical history
        if request.user.is_staff:
            return True
        
        # Check if user is in appropriate groups
        user_groups = request.user.groups.values_list('name', flat=True)
        allowed_groups = ['doctors', 'nurses', 'administrators']
        
        return any(group in user_groups for group in allowed_groups)


class CanUploadDocuments(permissions.BasePermission):
    """
    Permission to upload patient documents.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Staff can upload documents
        if request.user.is_staff:
            return True
        
        # Check if user is in appropriate groups
        user_groups = request.user.groups.values_list('name', flat=True)
        allowed_groups = ['doctors', 'nurses', 'receptionists', 'administrators']
        
        return any(group in user_groups for group in allowed_groups)


class CanExportData(permissions.BasePermission):
    """
    Permission to export patient data.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Staff can export data
        if request.user.is_staff:
            return True
        
        # Check if user is in appropriate groups
        user_groups = request.user.groups.values_list('name', flat=True)
        allowed_groups = ['administrators', 'receptionists']
        
        return any(group in user_groups for group in allowed_groups)


class CanViewAuditLogs(permissions.BasePermission):
    """
    Permission to view audit logs.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Staff can view all audit logs
        if request.user.is_staff:
            return True
        
        # Check if user is in administrator group
        user_groups = request.user.groups.values_list('name', flat=True)
        return 'administrators' in user_groups


class RoleBasedPermission(permissions.BasePermission):
    """
    Generic role-based permission checker.
    """
    
    def __init__(self, allowed_roles=None):
        self.allowed_roles = allowed_roles or []
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Staff have all permissions
        if request.user.is_staff:
            return True
        
        # Check if user is in any of the allowed roles
        user_groups = request.user.groups.values_list('name', flat=True)
        return any(role in user_groups for role in self.allowed_roles)
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


def get_user_permissions(user):
    """
    Get all permissions for a user based on their groups and staff status.
    """
    permissions = {
        'can_view_patients': False,
        'can_edit_patients': False,
        'can_delete_patients': False,
        'can_view_medical_history': False,
        'can_edit_medical_history': False,
        'can_upload_documents': False,
        'can_export_data': False,
        'can_view_audit_logs': False,
        'is_staff': user.is_staff,
    }
    
    if user.is_staff:
        # Staff have all permissions
        for key in permissions:
            if key != 'is_staff':
                permissions[key] = True
        return permissions
    
    # Check user groups
    user_groups = user.groups.values_list('name', flat=True)
    
    # Basic patient access
    if any(group in user_groups for group in ['doctors', 'nurses', 'receptionists', 'administrators']):
        permissions['can_view_patients'] = True
    
    # Patient editing
    if any(group in user_groups for group in ['doctors', 'nurses', 'receptionists', 'administrators']):
        permissions['can_edit_patients'] = True
    
    # Patient deletion
    if 'administrators' in user_groups:
        permissions['can_delete_patients'] = True
    
    # Medical history access
    if any(group in user_groups for group in ['doctors', 'nurses', 'administrators']):
        permissions['can_view_medical_history'] = True
        permissions['can_edit_medical_history'] = True
    
    # Document upload
    if any(group in user_groups for group in ['doctors', 'nurses', 'receptionists', 'administrators']):
        permissions['can_upload_documents'] = True
    
    # Data export
    if any(group in user_groups for group in ['administrators', 'receptionists']):
        permissions['can_export_data'] = True
    
    # Audit logs
    if 'administrators' in user_groups:
        permissions['can_view_audit_logs'] = True
    
    return permissions
