from django.utils.deprecation import MiddlewareMixin
import time
import sentry_sdk

class PerformanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log a Sentry si es muy lento
            if duration > 3.0:  # Más de 3 segundos
                sentry_sdk.capture_message(
                    f"Slow request: {request.path}",
                    level="warning",
                    extra={
                        "duration": duration,
                        "method": request.method,
                        "user": request.user.username if request.user.is_authenticated else "anonymous"
                    }
                )
            
            # Agregar header
            response['X-Request-Time'] = f"{duration:.3f}s"
        
        return response