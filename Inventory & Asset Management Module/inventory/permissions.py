"""
Inventory permissions
"""
from rest_framework.permissions import BasePermission


class IsInventoryAdmin(BasePermission):
    """Permission for inventory administrators"""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_staff or 
             request.user.groups.filter(name='Inventory Admin').exists() or
             request.user.has_perm('inventory.can_manage_inventory'))
        )


class IsInventoryUser(BasePermission):
    """Permission for inventory users (read and basic operations)"""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_staff or 
             request.user.groups.filter(name__in=['Inventory Admin', 'Inventory User']).exists() or
             request.user.has_perm('inventory.can_view_inventory'))
        )
    
    def has_object_permission(self, request, view, obj):
        # Allow read access to all authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # For write operations, check if user is admin or has specific permissions
        return (
            request.user.is_staff or
            request.user.groups.filter(name='Inventory Admin').exists() or
            request.user.has_perm('inventory.can_manage_inventory')
        )
