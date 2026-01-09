"""
Custom middleware for the inventory application.
"""
from .signals import set_current_user, set_current_ip


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AuditMiddleware:
    """
    Middleware to set current user and IP address for audit logging.
    This allows signals to access the request context.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set user and IP for audit logging
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)

        set_current_ip(get_client_ip(request))

        response = self.get_response(request)

        # Clean up
        set_current_user(None)
        set_current_ip(None)

        return response


class RateLimitMiddleware:
    """
    Simple rate limiting middleware for API endpoints.
    Limits requests per IP address.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache = {}  # In production, use Redis
        self.rate_limit = 100  # requests per minute
        self.window = 60  # seconds

    def __call__(self, request):
        from django.http import JsonResponse
        from time import time

        # Only rate limit API endpoints
        if request.path.startswith('/api/'):
            ip = get_client_ip(request)
            current_time = time()

            if ip in self.cache:
                requests, window_start = self.cache[ip]
                if current_time - window_start > self.window:
                    # Reset window
                    self.cache[ip] = (1, current_time)
                elif requests >= self.rate_limit:
                    return JsonResponse(
                        {'error': 'Rate limit exceeded. Please try again later.'},
                        status=429
                    )
                else:
                    self.cache[ip] = (requests + 1, window_start)
            else:
                self.cache[ip] = (1, current_time)

        return self.get_response(request)
