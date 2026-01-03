from django.test import TestCase
from django.core.management import call_command
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import Vehicle, Vigencia
from reminders.models import NotificationLog
from datetime import date, timedelta
from io import StringIO

class SendRemindersCommandTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            alias='Test Vehicle'
        )
    
    def test_send_reminders_for_today(self):
        # Crear vigencia que vence hoy
        vigencia = Vigencia.objects.create(
            vehicle=self.vehicle,
            tipo='SOAT',
            fecha_vencimiento=date.today(),
            activo=True,
            r1=True
        )
        
        out = StringIO()
        call_command('send_reminders', stdout=out)
        
        # Verificar que se creó un NotificationLog
        self.assertEqual(NotificationLog.objects.count(), 1)
        log = NotificationLog.objects.first()
        self.assertEqual(log.vigencia, vigencia)
        self.assertEqual(log.channel, 'EMAIL')
        self.assertEqual(log.status, 'SENT')
        
        # Verificar output del comando
        self.assertIn('Listo. Enviados=', out.getvalue())
    
    def test_send_reminders_for_7_days(self):
        # Crear vigencia que vence en 7 días
        vigencia = Vigencia.objects.create(
            vehicle=self.vehicle,
            tipo='TECNO',
            fecha_vencimiento=date.today() + timedelta(days=7),
            activo=True,
            r7=True
        )
        
        out = StringIO()
        call_command('send_reminders', stdout=out)
        
        self.assertEqual(NotificationLog.objects.count(), 1)
    
    def test_no_email_skipped(self):
        # Crear usuario sin email
        user_no_email = User.objects.create_user(
            username='noemail',
            password='testpass123',
            email=''
        )
        vehicle = Vehicle.objects.create(
            owner=user_no_email,
            alias='No Email Vehicle'
        )
        vigencia = Vigencia.objects.create(
            vehicle=vehicle,
            tipo='SOAT',
            fecha_vencimiento=date.today(),
            activo=True,
            r1=True
        )
        
        out = StringIO()
        call_command('send_reminders', stdout=out)
        
        # Debería estar SKIPPED
        log = NotificationLog.objects.filter(vigencia=vigencia).first()
        self.assertEqual(log.status, 'SKIPPED')
        self.assertIn('Usuario sin email', log.message)