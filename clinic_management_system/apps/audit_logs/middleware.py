"""
Audit Logging Middleware

This middleware automatically logs user actions and system events.
"""

import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import AuditLog, SystemEventLog

logger = logging.getLogger(__name__)


class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log user actions and system events.
    """
    
    def process_request(self, request):
        """Process the request and extract relevant information"""
        request.audit_data = {
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'request_path': request.path,
            'request_method': request.method,
        }
    
    def process_response(self, request, response):
        """Process the response and log if necessary"""
        # Only log for authenticated users
        if not hasattr(request, 'user') or isinstance(request.user, AnonymousUser):
            return response
        
        # Log certain actions
        if self.should_log_request(request, response):
            try:
                self.log_request(request, response)
            except Exception as e:
                logger.error(f"Failed to log audit entry: {e}")
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions and errors"""
        if not hasattr(request, 'user') or isinstance(request.user, AnonymousUser):
            return None
        
        try:
            SystemEventLog.objects.create(
                event_type='error',
                user=request.user,
                title=f"Exception in {request.path}",
                description=str(exception),
                module='patient_management',
                request_data={
                    'path': request.path,
                    'method': request.method,
                    'user': request.user.username,
                }
            )
        except Exception as e:
            logger.error(f"Failed to log exception: {e}")
        
        return None
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def should_log_request(self, request, response):
        """Determine if this request should be logged"""
        # Log API requests
        if request.path.startswith('/api/'):
            return True
        
        # Log admin actions
        if request.path.startswith('/admin/'):
            return True
        
        # Log patient-related actions
        if 'patient' in request.path.lower():
            return True
        
        return False
    
    def log_request(self, request, response):
        """Log the request details"""
        action = self.determine_action(request)
        
        AuditLog.objects.create(
            user=request.user,
            action=action,
            description=f"{request.method} {request.path}",
            ip_address=request.audit_data['ip_address'],
            user_agent=request.audit_data['user_agent'],
            request_path=request.audit_data['request_path'],
            request_method=request.audit_data['request_method'],
            additional_data={
                'response_status': response.status_code,
                'content_type': response.get('Content-Type', ''),
            }
        )
    
    def determine_action(self, request):
        """Determine the action type based on the request"""
        if request.method == 'GET':
            return 'view'
        elif request.method == 'POST':
            return 'create'
        elif request.method in ['PUT', 'PATCH']:
            return 'update'
        elif request.method == 'DELETE':
            return 'delete'
        else:
            return 'view'
