import logging

logger = logging.getLogger(__name__)


class OAuthDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log all OAuth-related requests
        if 'google' in request.path or 'social' in request.path or 'callback' in request.path:
            logger.info(f"OAuth Request: {request.method} {request.path}")
            logger.info(f"GET params: {dict(request.GET)}")
            logger.info(f"User authenticated: {request.user.is_authenticated if hasattr(request, 'user') else 'No user'}")
            
        response = self.get_response(request)
        
        # Log OAuth responses
        if 'google' in request.path or 'social' in request.path or 'callback' in request.path:
            logger.info(f"OAuth Response: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            if hasattr(response, 'url'):
                logger.info(f"Redirect URL: {response.url}")
            if hasattr(request, 'user'):
                logger.info(f"User after request: {request.user.is_authenticated}")
            
            # Log response content for 200 responses (error pages)
            if response.status_code == 200 and 'callback' in request.path:
                content = response.content.decode('utf-8')[:500]  # First 500 chars
                logger.info(f"Response content preview: {content}")
                
        return response