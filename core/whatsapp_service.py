from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
    
    def send_reminder(self, to_phone, vigencia, days_left):
        """Envía recordatorio por WhatsApp"""
        try:
            vehicle = vigencia.vehicle
            tipo = vigencia.get_tipo_display()
            
            # Plantilla aprobada por WhatsApp
            if days_left == 0:
                message = f"""
*🚨 URGENTE: {tipo} VENCE HOY*

📋 Documento: {tipo}
🚗 Vehículo: {vehicle.alias}
📅 Fecha vencimiento: HOY
🔗 Renueva aquí: {settings.BASE_URL}

_Mis Vigencias - Recordatorios automáticos_
"""
            elif days_left <= 7:
                message = f"""
*⚠️ Recordatorio: {tipo} por vencer*

📋 Documento: {tipo}
🚗 Vehículo: {vehicle.alias}
📅 Vence en: {days_left} días
🗓️ Fecha: {vigencia.fecha_vencimiento}
🔗 Ver detalles: {settings.BASE_URL}

_Mis Vigencias - Recordatorios automáticos_
"""
            else:
                message = f"""
*📅 Recordatorio: {tipo}*

📋 Documento: {tipo}
🚗 Vehículo: {vehicle.alias}
📅 Vence en: {days_left} días
🗓️ Fecha: {vigencia.fecha_vencimiento}
🔗 Ver detalles: {settings.BASE_URL}

_Mis Vigencias - Recordatorios automáticos_
"""
            
            # Enviar mensaje
            response = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=f"whatsapp:{to_phone}"
            )
            
            logger.info(f"WhatsApp enviado a {to_phone}: {response.sid}")
            return True, response.sid
            
        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {str(e)}")
            return False, str(e)
    
    def send_welcome(self, to_phone, username):
        """Envía mensaje de bienvenida"""
        try:
            message = f"""
*¡Bienvenido a Mis Vigencias, {username}!* 👋

Ahora recibirás recordatorios de tus documentos vehiculares:
• SOAT
• Tecnomecánica
• Seguros
• Impuestos

📱 *Configuración recomendada:*
1. Guarda este número como contacto
2. Activa notificaciones
3. Agrega tus vehículos en la app

¿Necesitas ayuda? Responde a este mensaje.

_Mis Vigencias - Tus documentos al día_
"""
            
            response = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=f"whatsapp:{to_phone}"
            )
            
            return True, response.sid
            
        except Exception as e:
            return False, str(e)