from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone

from core.models import Vigencia, PlanChoices
from reminders.models import NotificationLog, ChannelChoices, StatusChoices


class Command(BaseCommand):
    help = "Envía recordatorios de vigencias (30/15/7/1 días) por email. WhatsApp solo PRO (pendiente)."

    def handle(self, *args, **options):
        today = timezone.localdate()
        sent = 0
        skipped = 0
        failed = 0

        qs = Vigencia.objects.filter(activo=True).select_related("vehicle", "vehicle__owner")

        for v in qs:
            owner = v.vehicle.owner
            email = owner.email or ""
            if not email:
                NotificationLog.objects.create(
                    vigencia=v,
                    channel=ChannelChoices.EMAIL,
                    status=StatusChoices.SKIPPED,
                    message="Usuario sin email",
                )
                skipped += 1
                continue

            days_left = (v.fecha_vencimiento - today).days

            # Solo estos días enviamos
            should_send = (
                (days_left == 30 and v.r30) or
                (days_left == 15 and v.r15) or
                (days_left == 7 and v.r7) or
                (days_left == 1 and v.r1) or
                (days_left == 0)  # hoy vence
            )

            if not should_send:
                continue

            subject = f"[Mis Vigencias] {v.get_tipo_display()} vence en {days_left} día(s)"
            body = (
                f"Hola {owner.username},\n\n"
                f"Te recordamos que tu {v.get_tipo_display()} del vehículo '{v.vehicle.alias}' "
                f"vence el {v.fecha_vencimiento}.\n"
                f"Días restantes: {days_left}\n\n"
                f"Si ya renovaste, entra al dashboard y márcalo como 'Renové'.\n\n"
                f"— Mis Vigencias"
            )

            try:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=None,  # usa DEFAULT_FROM_EMAIL
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

        self.stdout.write(self.style.SUCCESS(
            f"Listo. Enviados={sent} | Omitidos={skipped} | Fallidos={failed}"
        ))
