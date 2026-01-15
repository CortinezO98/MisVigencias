from django.contrib import admin
from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("vigencia", "channel", "status", "created_at", "message")
    list_filter = ("channel", "status", "created_at")
    search_fields = ("vigencia__vehicle__alias", "vigencia__vehicle__plate")
    date_hierarchy = "created_at"   
    ordering = ("-created_at",)
    