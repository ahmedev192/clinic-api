"""
Rate limiting middleware for authentication endpoints.
"""
import time
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware for authentication endpoints.
    """
    
    def process_request(self, request):
        """Process the request and check rate limits."""
        # Only apply rate limiting to authentication endpoints
        if not request.path.startswith('/api/v1/auth/'):
            return None
        
        # Get client IP
        ip_address = self.get_client_ip(request)
        
        # Define rate limits for different endpoints
        rate_limits = {
            '/api/v1/auth/login/': {'requests': 5, 'window': 300},  # 5 requests per 5 minutes
            '/api/v1/auth/register/': {'requests': 3, 'window': 3600},  # 3 requests per hour
            '/api/v1/auth/password-reset/': {'requests': 3, 'window': 3600},  # 3 requests per hour
            '/api/v1/auth/verify-email/': {'requests': 10, 'window': 300},  # 10 requests per 5 minutes
        }
        
        # Check rate limit for the specific endpoint
        for endpoint, limits in rate_limits.items():
            if request.path.startswith(endpoint):
                if self.is_rate_limited(ip_address, endpoint, limits):
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': f'Too many requests. Please try again in {limits["window"]} seconds.',
                        'retry_after': limits['window']
                    }, status=429)
        
        return None
    
    def get_client_ip(self, request):
        """Get the client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, ip_address, endpoint, limits):
        """Check if the IP is rate limited for the endpoint."""
        cache_key = f"rate_limit:{ip_address}:{endpoint}"
        current_time = int(time.time())
        window_start = current_time - limits['window']
        
        # Get existing requests from cache
        requests = cache.get(cache_key, [])
        
        # Remove old requests outside the window
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # Check if limit is exceeded
        if len(requests) >= limits['requests']:
            return True
        
        # Add current request
        requests.append(current_time)
        cache.set(cache_key, requests, limits['window'])
        
        return False

