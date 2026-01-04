import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self):
        if not firebase_admin._apps:
            # Cargar credenciales desde variable de entorno
            cred_dict = json.loads(settings.FIREBASE_CREDENTIALS)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
    
    def send_push_notification(self, fcm_token, title, body, data=None):
        """Envía notificación push a un dispositivo"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=fcm_token,
            )
            
            response = messaging.send(message)
            logger.info(f"Push enviado: {response}")
            return True, response
            
        except Exception as e:
            logger.error(f"Error enviando push: {str(e)}")
            return False, str(e)
    
    def send_multicast(self, tokens, title, body, data=None):
        """Envía notificación a múltiples dispositivos"""
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=tokens,
            )
            
            response = messaging.send_multicast(message)
            logger.info(f"Multicast enviado: {response.success_count} éxitos")
            return True, response
            
        except Exception as e:
            logger.error(f"Error en multicast: {str(e)}")
            return False, str(e)
    
    def send_topic_notification(self, topic, title, body, data=None):
        """Envía notificación a un topic (ej: 'pro_users')"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                topic=topic,
            )
            
            response = messaging.send(message)
            return True, response
            
        except Exception as e:
            logger.error(f"Error en topic notification: {str(e)}")
            return False, str(e)