"""
Audit logging middleware.
"""
import time
import uuid
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from .models import APIAccessLog


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware for logging API access and performance metrics.
    """
    
    def process_request(self, request):
        """Process the request and start timing."""
        # Generate request ID
        request.request_id = str(uuid.uuid4())
        
        # Start timing
        request.start_time = time.time()
        
        # Count initial database queries
        request.initial_db_queries = len(connection.queries)
        
        # Count initial cache operations
        request.initial_cache_hits = getattr(request, 'cache_hits', 0)
        request.initial_cache_misses = getattr(request, 'cache_misses', 0)
    
    def process_response(self, request, response):
        """Process the response and log the API access."""
        # Only log API requests
        if not request.path.startswith('/api/'):
            return response
        
        # Calculate processing time
        processing_time = time.time() - getattr(request, 'start_time', time.time())
        
        # Count database queries
        db_queries = len(connection.queries) - getattr(request, 'initial_db_queries', 0)
        
        # Count cache operations
        cache_hits = getattr(request, 'cache_hits', 0) - getattr(request, 'initial_cache_hits', 0)
        cache_misses = getattr(request, 'cache_misses', 0) - getattr(request, 'initial_cache_misses', 0)
        
        # Get user
        user = getattr(request, 'user', None)
        if hasattr(user, 'is_authenticated') and not user.is_authenticated:
            user = None
        
        # Get request body (limit size)
        request_body = ''
        if hasattr(request, 'body'):
            body = request.body.decode('utf-8', errors='ignore')
            request_body = body[:10000]  # Limit to 10KB
        
        # Get response body (limit size)
        response_body = ''
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8', errors='ignore')
            response_body = content[:10000]  # Limit to 10KB
        
        # Create API access log
        APIAccessLog.objects.create(
            method=request.method,
            path=request.path,
            query_params=dict(request.GET),
            request_headers=dict(request.META),
            request_body=request_body,
            status_code=response.status_code,
            response_headers=dict(response),
            response_body=response_body,
            response_size=len(response.content) if hasattr(response, 'content') else 0,
            user=user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_key=request.session.session_key or '',
            request_id=getattr(request, 'request_id', ''),
            processing_time=processing_time,
            database_queries=db_queries,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
        )
        
        return response
    
    def get_client_ip(self, request):
        """Get the client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

