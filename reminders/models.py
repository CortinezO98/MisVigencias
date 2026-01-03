from django.db import models
from django.utils import timezone
from core.models import Vigencia


class ChannelChoices(models.TextChoices):
    EMAIL = "EMAIL", "Email"
    WHATSAPP = "WHATSAPP", "WhatsApp"


class StatusChoices(models.TextChoices):
    SENT = "SENT", "Enviado"
    FAILED = "FAILED", "Fallido"
    SKIPPED = "SKIPPED", "Omitido"


class NotificationLog(models.Model):
    vigencia = models.ForeignKey(Vigencia, on_delete=models.CASCADE, related_name="notification_logs")
    channel = models.CharField(max_length=12, choices=ChannelChoices.choices)
    status = models.CharField(max_length=10, choices=StatusChoices.choices)
    message = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.vigencia_id} {self.channel} {self.status} {self.created_at:%Y-%m-%d %H:%M}"
