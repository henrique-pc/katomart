from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from .models import (
    SystemConfig, Platform, PlatformURL, PlatformAuth, 
    Course, Module, Lesson, File, UserFormattedName, UserConfig
)


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    """Admin interface for System Configuration"""
    
    list_display = ('debug', 'download_path', 'ffmpeg_available', 'bento4_available', 'aria2c_available')
    list_filter = ('debug', 'ffmpeg_available', 'bento4_available', 'aria2c_available', 'geckodriver_available', 'chromedriver_available')
    readonly_fields = ('ffmpeg_available', 'bento4_available', 'aria2c_available', 'geckodriver_available', 'chromedriver_available', 'mkvtoolnix_available', 'rclone_available')
    
    fieldsets = (
        (_('General Settings'), {
            'fields': ('debug', 'download_path', 'should_download_drm_content')
        }),
        (_('Tool Paths'), {
            'fields': (
                ('ffmpeg_path', 'ffmpeg_available'),
                ('bento4_path', 'bento4_available'),
                ('aria2c_path', 'aria2c_available'),
                ('geckodriver_path', 'geckodriver_available'),
                ('chromedriver_path', 'chromedriver_available'),
                ('mkvtoolnix_path', 'mkvtoolnix_available'),
                ('rclone_path', 'rclone_available'),
            )
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one SystemConfig instance
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of SystemConfig
        return False


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    """Admin interface for Platforms"""
    
    list_display = ('name', 'id', 'base_url', 'active', 'may_have_issues', 'has_issues', 'created_at')
    list_filter = ('active', 'may_have_issues', 'has_issues', 'account_requires_specific_url', 'created_at')
    search_fields = ('name', 'id', 'base_url', 'issues_description')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('active', 'has_issues')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('id', 'name', 'base_url', 'active')
        }),
        (_('Configuration'), {
            'fields': ('account_requires_specific_url', 'url_description')
        }),
        (_('Issues'), {
            'fields': ('may_have_issues', 'has_issues', 'issues_description')
        }),
        (_('Additional Data'), {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlatformURL)
class PlatformURLAdmin(admin.ModelAdmin):
    """Admin interface for Platform URLs"""
    
    list_display = ('platform', 'url_kind', 'url', 'is_active', 'has_f_string', 'visitation_count', 'created_at')
    list_filter = ('platform', 'url_kind', 'is_active', 'has_f_string', 'needs_specific_headers', 'has_visitation_limit', 'created_at')
    search_fields = ('platform__name', 'url_kind', 'url', 'f_string_params')
    readonly_fields = ('created_at', 'updated_at', 'visitation_count')
    list_editable = ('is_active',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('id', 'platform', 'url_kind', 'url', 'is_active')
        }),
        (_('String Formatting'), {
            'fields': ('has_f_string', 'f_string_params')
        }),
        (_('Headers & Requests'), {
            'fields': ('needs_specific_headers', 'specific_headers', 'accepts_raw_request')
        }),
        (_('Visitation Limits'), {
            'fields': ('has_visitation_limit', 'visitation_limit', 'visitation_count')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlatformAuth)
class PlatformAuthAdmin(admin.ModelAdmin):
    """Admin interface for Platform Authentication"""
    
    list_display = ('platform', 'username', 'user', 'token_type', 'expires_at', 'created_at')
    list_filter = ('platform', 'token_type', 'expires_at', 'created_at')
    search_fields = ('platform__name', 'username', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Authentication'), {
            'fields': ('user', 'platform', 'username')
        }),
        (_('Encrypted Data'), {
            'fields': ('password_encrypted', 'token_encrypted', 'session_cookie_encrypted', 'refresh_token_encrypted'),
            'description': _('Encrypted credentials - these are encrypted at runtime and not stored in plain text')
        }),
        (_('Token Information'), {
            'fields': ('token_type', 'expires_at')
        }),
        (_('Additional Data'), {
            'fields': ('state', 'extra_data'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Courses"""
    
    list_display = ('name', 'teacher', 'platform', 'price', 'is_active', 'is_downloaded', 'has_drm', 'created_at')
    list_filter = ('platform', 'is_active', 'is_downloaded', 'has_drm', 'is_locked', 'course_expires', 'created_at')
    search_fields = ('name', 'teacher', 'description', 'external_id')
    readonly_fields = ('created_at', 'updated_at', 'katomart_id')
    list_editable = ('is_active', 'is_downloaded')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'formatted_name', 'teacher', 'description', 'price')
        }),
        (_('Identifiers'), {
            'fields': ('katomart_id', 'external_id')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_locked', 'unlocks_at', 'is_content_listed', 'content_list_date', 'content_list_type')
        }),
        (_('Download Information'), {
            'fields': ('is_downloaded', 'download_date', 'download_type', 'download_path')
        }),
        (_('Platform & Authentication'), {
            'fields': ('platform', 'auth')
        }),
        (_('DRM & Expiration'), {
            'fields': ('has_drm', 'course_expires', 'access_expiration')
        }),
        (_('Additional Data'), {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    """Admin interface for Modules"""
    
    list_display = ('name', 'course', 'order', 'is_active', 'is_downloaded', 'has_drm', 'created_at')
    list_filter = ('course__platform', 'is_active', 'is_downloaded', 'has_drm', 'is_locked', 'created_at')
    search_fields = ('name', 'description', 'external_id')
    readonly_fields = ('created_at', 'updated_at', 'katomart_id')
    list_editable = ('order', 'is_active', 'is_downloaded')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'formatted_name', 'description', 'order')
        }),
        (_('Identifiers'), {
            'fields': ('katomart_id', 'external_id')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_locked', 'unlocks_at', 'is_content_listed', 'content_list_date', 'content_list_type')
        }),
        (_('Download Information'), {
            'fields': ('should_download', 'is_downloaded', 'download_date', 'download_type')
        }),
        (_('Course'), {
            'fields': ('course',)
        }),
        (_('DRM'), {
            'fields': ('has_drm',)
        }),
        (_('Additional Data'), {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin interface for Lessons"""
    
    list_display = ('name', 'module', 'is_active', 'is_downloaded', 'has_drm', 'created_at')
    list_filter = ('module__course__platform', 'is_active', 'is_downloaded', 'has_drm', 'is_locked', 'created_at')
    search_fields = ('name', 'description', 'external_id')
    readonly_fields = ('created_at', 'updated_at', 'katomart_id')
    list_editable = ('is_active', 'is_downloaded')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'formatted_name', 'description')
        }),
        (_('Identifiers'), {
            'fields': ('katomart_id', 'external_id')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_locked', 'unlocks_at', 'is_content_listed', 'content_list_date', 'content_list_type')
        }),
        (_('Download Information'), {
            'fields': ('should_download', 'is_downloaded', 'download_date', 'download_type')
        }),
        (_('Module'), {
            'fields': ('module',)
        }),
        (_('DRM'), {
            'fields': ('has_drm',)
        }),
        (_('Additional Data'), {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """Admin interface for Files"""
    
    list_display = ('name', 'lesson', 'order', 'is_primary_content', 'is_extra_content', 'file_type', 'file_size', 'is_downloaded', 'has_drm', 'created_at')
    list_filter = ('lesson__module__course__platform', 'is_primary_content', 'is_extra_content', 'file_type', 'is_downloaded', 'has_drm', 'is_decrypted', 'created_at')
    search_fields = ('name', 'description', 'external_id')
    readonly_fields = ('created_at', 'updated_at', 'katomart_id')
    list_editable = ('order', 'is_primary_content', 'is_extra_content', 'is_downloaded')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'formatted_name', 'description', 'order')
        }),
        (_('Identifiers'), {
            'fields': ('katomart_id', 'external_id')
        }),
        (_('Content Type'), {
            'fields': ('is_primary_content', 'is_extra_content')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_locked', 'unlocks_at', 'should_download')
        }),
        (_('File Information'), {
            'fields': ('file_type', 'file_size', 'duration')
        }),
        (_('Download & DRM'), {
            'fields': ('is_downloaded', 'download_date', 'has_drm', 'is_decrypted')
        }),
        (_('Lesson'), {
            'fields': ('lesson',)
        }),
        (_('Additional Data'), {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserFormattedName)
class UserFormattedNameAdmin(admin.ModelAdmin):
    """Admin interface for User Formatted Names"""
    
    list_display = ('user', 'content_type', 'object_id', 'formatted_name')
    list_filter = ('content_type',)
    search_fields = ('user__username', 'formatted_name')
    readonly_fields = ()
    
    fieldsets = (
        (_('User Formatted Name'), {
            'fields': ('user', 'content_type', 'object_id', 'formatted_name')
        }),
    )


@admin.register(UserConfig)
class UserConfigAdmin(admin.ModelAdmin):
    """Admin interface for User Configuration"""
    
    list_display = ('user', 'download_path', 'ffmpeg_path', 'bento4_path', 'aria2c_path')
    search_fields = ('user__username', 'download_path')
    readonly_fields = ()
    
    fieldsets = (
        (_('User'), {
            'fields': ('user',)
        }),
        (_('Paths'), {
            'fields': ('download_path', 'ffmpeg_path', 'bento4_path', 'aria2c_path', 'geckodriver_path', 'chromedriver_path', 'mkvtoolnix_path', 'rclone_path')
        }),
    )


# Customize admin site
admin.site.site_header = _('KatoMart Administration')
admin.site.site_title = _('KatoMart Admin Portal')
admin.site.index_title = _('Welcome to KatoMart Administration')
