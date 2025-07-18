from django.db import models
import uuid

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Config(models.Model):
    """
    Single-row table for global configuration.
    """
    debug = models.BooleanField(default=False)  # type: ignore[attr-defined]
    download_path = models.CharField(max_length=512, default="downloads")
    port = models.PositiveIntegerField(default=6102)  # type: ignore[attr-defined]
    katomart_url = models.CharField(max_length=256, default="https://katomart.com")
    JWT_SECRET_KEY = models.CharField(max_length=64, default="33d4498fe55a8fca179d20a4ae596fc4bf8d8fa5")
    webui_pass = models.CharField(max_length=128, default="admin")
    external_tools = models.JSONField(default=dict, blank=True)
    should_download_drm_content = models.BooleanField(default=False)  # type: ignore[attr-defined]

    def save(self, *args, **kwargs):
        # Always enforce single row (id=1)
        if not self.pk:
            self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)  # type: ignore[attr-defined]
        return obj

class Platform(TimestampMixin):
    id = models.CharField(primary_key=True, max_length=64)  # Slug or UUID
    name = models.CharField(max_length=256, null=True, blank=True)
    base_url = models.CharField(max_length=512, null=True, blank=True)
    active = models.BooleanField(default=True)  # type: ignore[attr-defined]
    account_requires_specific_url = models.BooleanField(default=False)  # type: ignore[attr-defined]
    url_description = models.CharField(max_length=512, null=True, blank=True)
    may_have_issues = models.BooleanField(default=False)  # type: ignore[attr-defined]
    has_issues = models.BooleanField(default=False)  # type: ignore[attr-defined]
    issues_description = models.CharField(max_length=512, null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

class PlatformURL(TimestampMixin):
    id = models.CharField(primary_key=True, max_length=64)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name="urls")
    url_kind = models.CharField(max_length=64, null=True, blank=True)  # e.g. login, dashboard, api, product
    has_f_string = models.BooleanField(default=False)  # type: ignore[attr-defined]
    f_string_params = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)  # type: ignore[attr-defined]
    needs_specific_headers = models.BooleanField(default=False)  # type: ignore[attr-defined]
    specific_headers = models.TextField(null=True, blank=True)
    accepts_raw_request = models.BooleanField(default=False)  # type: ignore[attr-defined]
    has_visitation_limit = models.BooleanField(default=False)  # type: ignore[attr-defined]
    visitation_limit = models.IntegerField(null=True, blank=True)  # type: ignore[attr-defined] 
    visitation_count = models.IntegerField(default=0)  # type: ignore[attr-defined]
    url = models.CharField(max_length=1024, null=True, blank=True)

class PlatformAuth(TimestampMixin):
    id = models.AutoField(primary_key=True)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name="auths")
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=256)  # Plain text for third-party login
    token = models.CharField(max_length=512, null=True, blank=True)
    refresh_token = models.CharField(max_length=512, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

class Course(TimestampMixin):
    internal_id = models.AutoField(primary_key=True)
    katomart_id = models.UUIDField(null=True, blank=True, default=None)
    external_id = models.CharField(max_length=128, null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    formatted_name = models.CharField(max_length=256, null=True, blank=True)
    teacher = models.CharField(max_length=256, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_content_listed = models.BooleanField(default=False)  # type: ignore[attr-defined]
    content_list_date = models.BigIntegerField(null=True, blank=True)
    content_list_type = models.CharField(max_length=64, null=True, blank=True)
    is_downloaded = models.BooleanField(default=False)  # type: ignore[attr-defined]
    download_date = models.BigIntegerField(null=True, blank=True)
    download_type = models.CharField(max_length=64, null=True, blank=True)
    download_path = models.CharField(max_length=512, null=True, blank=True)
    is_active = models.BooleanField(default=False)  # type: ignore[attr-defined]
    is_locked = models.BooleanField(default=False)  # type: ignore[attr-defined]
    unlocks_at = models.BigIntegerField(null=True, blank=True)
    has_drm = models.BooleanField(default=False)  # type: ignore[attr-defined]
    course_expires = models.BooleanField(default=False)  # type: ignore[attr-defined]
    access_expiration = models.BigIntegerField(null=True, blank=True)
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")
    auth = models.ForeignKey(PlatformAuth, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")

class Module(TimestampMixin):
    internal_id = models.AutoField(primary_key=True)
    katomart_id = models.UUIDField(null=True, blank=True, default=None)
    external_id = models.CharField(max_length=128, null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    formatted_name = models.CharField(max_length=256, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)  # type: ignore[attr-defined]
    is_locked = models.BooleanField(default=False)  # type: ignore[attr-defined]
    unlocks_at = models.BigIntegerField(null=True, blank=True)
    has_drm = models.BooleanField(default=False)  # type: ignore[attr-defined]
    is_content_listed = models.BooleanField(default=False)  # type: ignore[attr-defined]
    content_list_date = models.BigIntegerField(null=True, blank=True)
    content_list_type = models.CharField(max_length=64, null=True, blank=True)
    should_download = models.BooleanField(default=True)  # type: ignore[attr-defined]
    is_downloaded = models.BooleanField(default=False)  # type: ignore[attr-defined]
    download_date = models.BigIntegerField(null=True, blank=True)
    download_type = models.CharField(max_length=64, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules", null=True, blank=True)

class Lesson(TimestampMixin):
    internal_id = models.AutoField(primary_key=True)
    katomart_id = models.UUIDField(null=True, blank=True, default=None)
    external_id = models.CharField(max_length=128, null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    formatted_name = models.CharField(max_length=256, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)  # type: ignore[attr-defined]
    is_locked = models.BooleanField(default=False)  # type: ignore[attr-defined]
    unlocks_at = models.BigIntegerField(null=True, blank=True)
    has_drm = models.BooleanField(default=False)  # type: ignore[attr-defined]
    is_content_listed = models.BooleanField(default=False)  # type: ignore[attr-defined]
    content_list_date = models.BigIntegerField(null=True, blank=True)
    content_list_type = models.CharField(max_length=64, null=True, blank=True)
    should_download = models.BooleanField(default=True)  # type: ignore[attr-defined]
    is_downloaded = models.BooleanField(default=False)  # type: ignore[attr-defined]
    download_date = models.BigIntegerField(null=True, blank=True)
    download_type = models.CharField(max_length=64, null=True, blank=True)
    module = models.ForeignKey('Module', on_delete=models.CASCADE, related_name="lessons", null=True, blank=True)

class File(TimestampMixin):
    internal_id = models.AutoField(primary_key=True)
    katomart_id = models.UUIDField(null=True, blank=True, default=None)
    external_id = models.CharField(max_length=128, null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    formatted_name = models.CharField(max_length=256, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    is_primary_content = models.BooleanField(default=False)  # type: ignore[attr-defined]
    is_extra_content = models.BooleanField(default=False)  # type: ignore[attr-defined]
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)  # type: ignore[attr-defined]
    is_locked = models.BooleanField(default=False)  # type: ignore[attr-defined]
    should_download = models.BooleanField(default=True)  # type: ignore[attr-defined]
    unlocks_at = models.BigIntegerField(null=True, blank=True)
    has_drm = models.BooleanField(default=False)  # type: ignore[attr-defined]
    is_decrypted = models.BooleanField(default=False)  # type: ignore[attr-defined]
    is_downloaded = models.BooleanField(default=False)  # type: ignore[attr-defined]
    download_date = models.BigIntegerField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=64, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name="files", null=True, blank=True)

def ensure_config_row_exists():
    """
    Ensure the single Config row exists in the database (id=1).
    Should be called at application startup.
    """
    from django.db import transaction
    with transaction.atomic():  # type: ignore
        Config.objects.get_or_create(pk=1)  # type: ignore[attr-defined]

def load_config():
    """
    Load the global configuration (single row).
    Returns the Config instance.
    """
    ensure_config_row_exists()
    return Config.objects.get(pk=1)  # type: ignore[attr-defined]

def save_config(**kwargs):
    """
    Update and save the global configuration (single row).
    Accepts keyword arguments for fields to update.
    Returns the updated Config instance.
    """
    config = load_config()
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    config.save()
    return config
