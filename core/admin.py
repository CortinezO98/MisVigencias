from django.contrib import admin
from .models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "whatsapp_enabled", "phone", "created_at")
    list_filter = ("plan", "whatsapp_enabled")
    search_fields = ("user__username", "user__email", "phone")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("alias", "plate", "owner", "created_at")
    search_fields = ("alias", "plate", "owner__username", "owner__email")
    list_filter = ("created_at",)


@admin.register(Vigencia)
class VigenciaAdmin(admin.ModelAdmin):
    list_display = ("tipo", "vehicle", "fecha_vencimiento", "activo", "created_at")
    list_filter = ("tipo", "activo")
    search_fields = ("vehicle__alias", "vehicle__plate", "vehicle__owner__username")
    date_hierarchy = "fecha_vencimiento"
    
    


@admin.register(OfficialService)
class OfficialServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "key", "is_active", "sort_order", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "key", "description", "url")
    ordering = ("sort_order", "title")
    prepopulated_fields = {"key": ("title",)}