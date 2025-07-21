from django.contrib import admin
from .models import Backup

@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "course", "backup_type", "status", "started_at", "completed_at")
    list_filter = ("backup_type", "status", "started_at", "completed_at")
    search_fields = ("user__username", "course__name", "backup_type", "status")
