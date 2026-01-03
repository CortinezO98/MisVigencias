from django.conf import settings
from django.db import models
from django.utils import timezone


class PlanChoices(models.TextChoices):
    FREE = "FREE", "Gratis"
    PRO = "PRO", "Pro"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    plan = models.CharField(max_length=10, choices=PlanChoices.choices, default=PlanChoices.FREE)
    phone = models.CharField(max_length=20, blank=True, default="")
    whatsapp_enabled = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perfil {self.user.username} ({self.plan})"


class Vehicle(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vehicles")
    alias = models.CharField(max_length=60)  
    plate = models.CharField(max_length=10, blank=True, default="") 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["alias"]

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
