from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging

logger = logging.getLogger('security')

class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Headers de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Log de seguridad
        if request.user.is_authenticated:
            logger.info(f"User {request.user.id} accessed {request.path}")
        
        return response