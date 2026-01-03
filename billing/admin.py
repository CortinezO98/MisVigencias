from django.contrib import admin
from .models import Subscription, Payment, PaymentMethod

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'days_until_expiry')
    list_filter = ('plan', 'status', 'start_date')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date', 'next_payment_date', 'last_payment_date')
        }),
        ('Límites', {
            'fields': ('max_vehicles', 'max_active_vigencias')
        }),
        ('Información de Pago', {
            'fields': ('payment_method',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscription', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('subscription__user__username', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información del Pago', {
            'fields': ('subscription', 'amount', 'currency', 'status')
        }),
        ('Detalles de Transacción', {
            'fields': ('transaction_id', 'payment_method', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'method_type', 'last_four', 'is_default', 'created_at')
    list_filter = ('method_type', 'is_default')
    search_fields = ('user__username', 'identifier')