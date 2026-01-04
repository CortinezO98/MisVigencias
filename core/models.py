from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from .validators import validar_placa_colombiana
from django.core.validators import RegexValidator
from django.core.validators import FileExtensionValidator



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



class OfficialService(models.Model):
    """
    Enlaces a servicios oficiales (SIMIT, RUNT, etc.) administrables desde Django Admin.
    Se muestran en el dashboard como "Consultas oficiales".
    """

    key = models.SlugField(
        max_length=50,
        unique=True,
        help_text="Identificador único (ej: simit, runt_placa)."
    )
    title = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=500)

    # Bootstrap Icons class (ej: bi-receipt-cutoff)
    icon = models.CharField(
        max_length=80,
        default="bi-link-45deg",
        validators=[
            RegexValidator(
                regex=r"^bi-[a-z0-9-]+$",
                message="El icono debe ser una clase Bootstrap Icons tipo: bi-receipt-cutoff",
            )
        ],
        help_text="Clase de Bootstrap Icons. Ej: bi-receipt-cutoff"
    )

    note = models.CharField(max_length=255, blank=True)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "title"]
        indexes = [
            models.Index(fields=["is_active", "sort_order"]),
        ]
        verbose_name = "Servicio oficial"
        verbose_name_plural = "Servicios oficiales"

    def __str__(self) -> str:
        return f"{self.title} ({'Activo' if self.is_active else 'Inactivo'})"


class Documento(models.Model):
    """Documentos adjuntos a vigencias"""
    vigencia = models.ForeignKey(Vigencia, on_delete=models.CASCADE, related_name="documentos")
    nombre = models.CharField(max_length=255)
    archivo = models.FileField(
        upload_to='documentos/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'heic']
            )
        ],
        max_length=500
    )
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('SOAT', 'SOAT'),
            ('TECNO', 'Tecnomecánica'),
            ('SEGURO', 'Seguro'),
            ('POLIZA', 'Póliza'),
            ('FACTURA', 'Factura'),
            ('OTRO', 'Otro'),
        ]
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_documento = models.DateField(null=True, blank=True)
    es_valido = models.BooleanField(default=True)
    notas = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-fecha_documento', '-fecha_subida']
    
    def __str__(self):
        return f"{self.nombre} - {self.vigencia}"
    
    def extension(self):
        return os.path.splitext(self.archivo.name)[1].lower()
    
    def es_imagen(self):
        return self.extension() in ['.jpg', '.jpeg', '.png', '.heic']
    
    def es_pdf(self):
        return self.extension() == '.pdf'
    
    


class FCMToken(models.Model):
    """Tokens Firebase Cloud Messaging por usuario/dispositivo"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="fcm_tokens"
    )
    token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('ANDROID', 'Android'),
            ('IOS', 'iOS'),
            ('WEB', 'Web'),
        ],
        default='ANDROID'
    )
    device_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.device_type}"