from django.db import models
from django.conf import settings
from core.models import Course

# Create your models here.

class Backup(models.Model):
    BACKUP_TYPE_CHOICES = [
        ("telegram", "Telegram"),
        ("rclone", "Rclone"),
        # Add more types as needed
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="backups")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="backups")
    backup_type = models.CharField(max_length=32, choices=BACKUP_TYPE_CHOICES)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    backup_location = models.CharField(max_length=512, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-started_at"]
        unique_together = ("user", "course", "backup_type", "started_at")

    def __str__(self):
        return f"Backup({self.user}, {self.course}, {self.backup_type}, {self.status})"
