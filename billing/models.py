from django.conf import settings
from django.db import models
from django.utils import timezone

class SubscriptionPlan(models.TextChoices):
    FREE = "FREE", "Gratis"
    PRO = "PRO", "Profesional"
    BUSINESS = "BUSINESS", "Empresarial"

class SubscriptionStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Activa"
    CANCELED = "CANCELED", "Cancelada"
    EXPIRED = "EXPIRED", "Expirada"
    PENDING = "PENDING", "Pendiente"

class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pendiente"
    COMPLETED = "COMPLETED", "Completado"
    FAILED = "FAILED", "Fallido"
    REFUNDED = "REFUNDED", "Reembolsado"

class Subscription(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="subscription"
    )
    plan = models.CharField(
        max_length=20, 
        choices=SubscriptionPlan.choices, 
        default=SubscriptionPlan.FREE
    )
    status = models.CharField(
        max_length=20, 
        choices=SubscriptionStatus.choices, 
        default=SubscriptionStatus.ACTIVE
    )
    
    # Fechas de suscripción
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Información de pago
    payment_method = models.CharField(max_length=50, blank=True, default="")
    last_payment_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)
    
    # Límites según plan
    max_vehicles = models.IntegerField(default=1)
    max_active_vigencias = models.IntegerField(default=3)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['end_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()}"
    
    @property
    def is_active(self):
        return self.status == SubscriptionStatus.ACTIVE
    
    @property
    def days_until_expiry(self):
        if self.end_date:
            return (self.end_date.date() - timezone.now().date()).days
        return None

class Payment(models.Model):
    subscription = models.ForeignKey(
        Subscription, 
        on_delete=models.CASCADE, 
        related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="COP")
    status = models.CharField(
        max_length=20, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )
    
    # Información de transacción
    transaction_id = models.CharField(max_length=100, blank=True, default="")
    payment_method = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscription', 'status']),
            models.Index(fields=['transaction_id']),
        ]
    
    def __str__(self):
        return f"Pago #{self.id} - {self.amount} {self.currency}"

class PaymentMethod(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="payment_methods"
    )
    method_type = models.CharField(max_length=20)  # nequi, daviplata, card
    identifier = models.CharField(max_length=100)  # número, token
    is_default = models.BooleanField(default=False)
    
    # Información adicional
    last_four = models.CharField(max_length=4, blank=True, default="")
    expiry_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'method_type', 'identifier']
    
    def __str__(self):
        return f"{self.user.username} - {self.method_type}"