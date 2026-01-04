import sentry_sdk
from django.conf import settings
import logging
import time

logger = logging.getLogger(__name__)

def track_performance(view_func):
    """Decorador para monitorear performance"""
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        
        try:
            response = view_func(request, *args, **kwargs)
            
            # Registrar tiempo de respuesta
            response_time = time.time() - start_time
            
            if response_time > 2.0:  # Más de 2 segundos
                sentry_sdk.capture_message(
                    f"Slow response: {request.path} - {response_time:.2f}s",
                    level="warning"
                )
            
            # Agregar header de performance
            response['X-Response-Time'] = f"{response_time:.3f}s"
            
            return response
            
        except Exception as e:
            # Capturar excepción en Sentry
            sentry_sdk.capture_exception(e)
            raise
    
    return wrapper

def log_user_activity(user, action, details=None):
    """Log de actividad de usuario"""
    sentry_sdk.set_user({
        "id": user.id,
        "username": user.username,
        "email": user.email
    })
    
    sentry_sdk.capture_message(
        f"User Activity: {user.username} - {action}",
        level="info",
        extra=details or {}
    )
    
    logger.info(f"User {user.id} - {action}")

def monitor_database_queries():
    """Monitorear queries lentos"""
    from django.db import connection
    from django.conf import settings
    
    if len(connection.queries) > 50:
        sentry_sdk.capture_message(
            f"High query count: {len(connection.queries)}",
            level="warning"
        )
    
    for query in connection.queries:
        if float(query['time']) > 1.0:  # Más de 1 segundo
            sentry_sdk.capture_message(
                "Slow database query",
                level="warning",
                extra={
                    "query": query['sql'][:200],
                    "time": query['time']
                }
            )