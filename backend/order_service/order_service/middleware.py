"""
Custom middleware to allow Docker service names as hostnames
"""


class DisableHostCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip host validation for internal service calls
        request.META['HTTP_HOST'] = request.META.get('HTTP_HOST', 'localhost')
        
        # Force Django to accept any host by setting a valid one
        if '_' in request.META['HTTP_HOST'] or ':' in request.META['HTTP_HOST']:
            # Replace with localhost to pass validation
            request.META['HTTP_HOST'] = 'localhost'
        
        response = self.get_response(request)
        return response
