from django.db import models
from django.conf import settings
from core.models import File, Module, Lesson
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class VideoNote(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="video_notes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="video_notes")
    time = models.FloatField(help_text="Time in seconds")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("file", "user", "time")

    def __str__(self):
        return f"VideoNote({self.file}, {self.user}, {self.time}s)"

class PdfAnnotation(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="pdf_annotations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pdf_annotations")
    annotations = models.JSONField(help_text="List of annotation objects")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("file", "user")

    def __str__(self):
        return f"PdfAnnotation({self.file}, {self.user})"

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveSmallIntegerField(help_text="User rating 1-5")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "content_type", "object_id")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Rating({self.user}, {self.content_object}, {self.rating})"

class ViewCount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="view_counts")
    count = models.PositiveIntegerField(default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    last_viewed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "content_type", "object_id")
        ordering = ["-last_viewed"]

    def __str__(self):
        return f"ViewCount({self.user}, {self.content_object}, {self.count})"
