"""
Audit middleware for tracking user actions
"""
import threading
from django.utils.deprecation import MiddlewareMixin


class AuditMiddleware(MiddlewareMixin):
    """Middleware to store request in thread local storage for audit logging"""
    
    def process_request(self, request):
        """Store request in thread local storage"""
        threading.current_thread().request = request
        return None
