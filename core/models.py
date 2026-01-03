from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from .validators import validar_placa_colombiana



class PlanChoices(models.TextChoices):
    FREE = "FREE", "Gratis"
    PRO = "PRO", "Pro"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    plan = models.CharField(max_length=10, choices=PlanChoices.choices, default=PlanChoices.FREE)
    phone = models.CharField(max_length=20, blank=True, default="")
    whatsapp_enabled = models.BooleanField(default=False) 
    whatsapp_notifications = models.BooleanField(default=True)  
    email_notifications = models.BooleanField(default=True)    
    notification_days = models.JSONField(default=list)         
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)           

    def __str__(self):
        return f"Perfil {self.user.username} ({self.plan})"
    
    def save(self, *args, **kwargs):
        if not self.notification_days:
            self.notification_days = [30, 15, 7, 1]
        super().save(*args, **kwargs)


class Vehicle(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vehicles")
    alias = models.CharField(max_length=60, validators=[MinLengthValidator(2)])
    plate = models.CharField(
        max_length=10, 
        blank=True, 
        default="",
        validators=[validar_placa_colombiana]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["alias"]
        indexes = [
            models.Index(fields=['owner', 'created_at']),
            models.Index(fields=['plate']),
        ]

    def __str__(self):
        return f"{self.alias} ({self.plate})" if self.plate else self.alias


class VigenciaType(models.TextChoices):
    SOAT = "SOAT", "SOAT"
    TECNO = "TECNO", "Tecnomecánica"
    SEGURO = "SEGURO", "Seguro"
    IMPUESTO = "IMPUESTO", "Impuesto"
    OTRO = "OTRO", "Otro"


class Vigencia(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="vigencias")
    tipo = models.CharField(max_length=12, choices=VigenciaType.choices)
    fecha_vencimiento = models.DateField()
    activo = models.BooleanField(default=True)
    r30 = models.BooleanField(default=True)
    r15 = models.BooleanField(default=True)
    r7 = models.BooleanField(default=True)
    r1 = models.BooleanField(default=True)

    last_notified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha_vencimiento"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.vehicle.alias} - {self.fecha_vencimiento}"

    def days_left(self) -> int:
        return (self.fecha_vencimiento - timezone.localdate()).days
