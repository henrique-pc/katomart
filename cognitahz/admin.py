from django.contrib import admin
from .models import VideoNote, PdfAnnotation, Rating, ViewCount

@admin.register(VideoNote)
class VideoNoteAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "user", "time", "created_at")
    list_filter = ("file", "user", "created_at")
    search_fields = ("file__name", "user__username", "text")

@admin.register(PdfAnnotation)
class PdfAnnotationAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "user", "created_at")
    list_filter = ("file", "user", "created_at")
    search_fields = ("file__name", "user__username")

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content_type", "object_id", "rating", "created_at")
    list_filter = ("content_type", "rating", "created_at")
    search_fields = ("user__username",)

@admin.register(ViewCount)
class ViewCountAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content_type", "object_id", "count", "last_viewed")
    list_filter = ("content_type", "last_viewed")
    search_fields = ("user__username",)
