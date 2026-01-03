# MODIFICAR reminders/management/commands/send_reminders.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from core.models import Vigencia, PlanChoices
from reminders.models import NotificationLog, ChannelChoices, StatusChoices


class Command(BaseCommand):
    help = "Envía recordatorios de vigencias (30/15/7/1 días) por email. WhatsApp solo PRO (pendiente)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Modo de prueba (no envía emails reales)',
        )
        parser.add_argument(
            '--days',
            type=int,
            help='Simular recordatorio para X días en el futuro',
        )

    def handle(self, *args, **options):
        today = timezone.localdate()
        
        # Si se especificó días, simular esa fecha
        if options['days']:
            today = today + timezone.timedelta(days=options['days'])
            self.stdout.write(f"Modo simulación: {today} (+{options['days']} días)")
        
        sent = 0
        skipped = 0
        failed = 0
        whatsapp_sent = 0

        qs = Vigencia.objects.filter(activo=True).select_related("vehicle", "vehicle__owner", "vehicle__owner__profile")

        for v in qs:
            owner = v.vehicle.owner
            profile = getattr(owner, 'profile', None)
            
            # ===== EMAIL =====
            email = owner.email or ""
            if email:
                days_left = (v.fecha_vencimiento - today).days
                
                should_send_email = (
                    (days_left == 30 and v.r30) or
                    (days_left == 15 and v.r15) or
                    (days_left == 7 and v.r7) or
                    (days_left == 1 and v.r1) or
                    (days_left == 0)  # hoy vence
                )
                
                if should_send_email:
                    if not options['test']:
                        try:
                            subject = f"[Mis Vigencias] {v.get_tipo_display()} vence en {days_left} día(s)"
                            body = (
                                f"Hola {owner.username},\n\n"
                                f"Te recordamos que tu {v.get_tipo_display()} del vehículo '{v.vehicle.alias}' "
                                f"vence el {v.fecha_vencimiento}.\n"
                                f"Días restantes: {days_left}\n\n"
                                f"Si ya renovaste, entra al dashboard y márcalo como 'Renové'.\n\n"
                                f"— Mis Vigencias"
                            )
                            
                            send_mail(
                                subject=subject,
                                message=body,
                                from_email=None,
                                recipient_list=[email],
                                fail_silently=False,
                            )
                            
                            NotificationLog.objects.create(
                                vigencia=v,
                                channel=ChannelChoices.EMAIL,
                                status=StatusChoices.SENT,
                                message=f"Email enviado a {email} (days_left={days_left})",
                            )
                            sent += 1
                            
                        except Exception as e:
                            NotificationLog.objects.create(
                                vigencia=v,
                                channel=ChannelChoices.EMAIL,
                                status=StatusChoices.FAILED,
                                message=str(e)[:255],
                            )
                            failed += 1
                    else:
                        # Modo prueba
                        self.stdout.write(
                            f"[TEST] Email para {owner.email}: {v.get_tipo_display()} "
                            f"vence en {days_left} días"
                        )
                        sent += 1
            
            else:
                NotificationLog.objects.create(
                    vigencia=v,
                    channel=ChannelChoices.EMAIL,
                    status=StatusChoices.SKIPPED,
                    message="Usuario sin email",
                )
                skipped += 1
            
            # ===== WHATSAPP (solo PRO) =====
            if profile and profile.plan == PlanChoices.PRO and profile.whatsapp_enabled and profile.phone:
                days_left = (v.fecha_vencimiento - today).days
                
                should_send_whatsapp = (
                    (days_left == 7 and v.r7) or
                    (days_left == 1 and v.r1) or
                    (days_left == 0)
                )
                
                if should_send_whatsapp:
                    # Simulación de envío WhatsApp
                    message = (
                        f"📱 Recordatorio Mis Vigencias:\n"
                        f"Tu {v.get_tipo_display()} del vehículo {v.vehicle.alias} "
                        f"vence el {v.fecha_vencimiento} ({days_left} días).\n"
                        f"Renueva a tiempo para evitar multas."
                    )
                    
                    if not options['test']:
                        # Aquí iría la integración real con Twilio/API de WhatsApp
                        # Por ahora solo registramos en logs
                        NotificationLog.objects.create(
                            vigencia=v,
                            channel=ChannelChoices.WHATSAPP,
                            status=StatusChoices.SENT,
                            message=f"WhatsApp simulado a {profile.phone}",
                        )
                    
                    whatsapp_sent += 1
                    self.stdout.write(
                        f"[WHATSAPP SIMULADO] {owner.username}: {message}"
                    )

        self.stdout.write(self.style.SUCCESS(
            f"Listo. Enviados={sent} | WhatsApp={whatsapp_sent} | "
            f"Omitidos={skipped} | Fallidos={failed}"
        ))