"""
Custom permissions for Staff Management
"""

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """
    def has_permission(self, request, view):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admins
        return request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to view/edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_staff:
            return True
        
        # Users can access their own staff profile
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # For staff objects, check if the user is the staff member
        if hasattr(obj, 'staff') and hasattr(obj.staff, 'user') and obj.staff.user == request.user:
            return True
        
        return False


class IsStaffOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow staff members or admins to perform actions.
    """
    def has_permission(self, request, view):
        # Admin users have full access
        if request.user.is_staff:
            return True
        
        # Check if user has a staff profile
        try:
            staff_profile = request.user.staff_profile
            return staff_profile.employment_status == 'active'
        except:
            return False
    
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_staff:
            return True
        
        # Staff can only modify their own schedules
        if hasattr(obj, 'staff') and hasattr(obj.staff, 'user'):
            return obj.staff.user == request.user
        
        return False


class IsDoctorOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow doctors or admins to perform actions.
    """
    def has_permission(self, request, view):
        # Admin users have full access
        if request.user.is_staff:
            return True
        
        # Check if user is a doctor
        try:
            staff_profile = request.user.staff_profile
            return (staff_profile.employment_status == 'active' and 
                   staff_profile.role.code in ['DOC', 'DOCTOR'])
        except:
            return False


class CanViewStaffData(permissions.BasePermission):
    """
    Permission to view staff data based on role.
    """
    def has_permission(self, request, view):
        # Admin users have full access
        if request.user.is_staff:
            return True
        
        # Check if user has a staff profile
        try:
            staff_profile = request.user.staff_profile
            if staff_profile.employment_status != 'active':
                return False
            
            # Different roles have different access levels
            role_code = staff_profile.role.code
            
            # Admins and managers can view all staff
            if role_code in ['ADMIN', 'MANAGER']:
                return True
            
            # Doctors can view other doctors and nurses
            if role_code in ['DOC', 'DOCTOR']:
                return True
            
            # Nurses can view other nurses and doctors
            if role_code == 'NURSE':
                return True
            
            # Receptionists can view basic staff info
            if role_code == 'RECEPTIONIST':
                return True
            
            return False
        except:
            return False


class CanEditStaffData(permissions.BasePermission):
    """
    Permission to edit staff data based on role.
    """
    def has_permission(self, request, view):
        # Only admins can edit staff data
        return request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        # Only admins can edit staff data
        return request.user.is_staff
