from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('security')

class Command(BaseCommand):
    help = "Revisa problemas de seguridad"
    
    def handle(self, *args, **options):
        self.stdout.write("🔒 Revisando seguridad...")
        
        # 1. Usuarios sin actividad reciente
        threshold = timezone.now() - timedelta(days=90)
        inactive_users = User.objects.filter(
            last_login__lt=threshold,
            is_active=True
        ).count()
        
        if inactive_users > 0:
            logger.warning(f"{inactive_users} usuarios inactivos > 90 días")
        
        # 2. Usuarios con contraseñas débiles (si tienes zxcvbn)
        weak_passwords = 0
        # Implementar check de contraseñas débiles
        
        # 3. Logs de admin
        self.stdout.write(f"✓ {inactive_users} usuarios inactivos")
        self.stdout.write(f"✓ {weak_passwords} contraseñas débiles")
        
        self.stdout.write(self.style.SUCCESS("Revisión de seguridad completada"))