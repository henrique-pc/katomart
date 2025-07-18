from django.db import models
import uuid
from django.contrib.auth import get_user_model
from cryptography.fernet import Fernet, InvalidToken
import base64
import json
import re
import os
from pathlib import Path
import shutil

User = get_user_model()

# Encryption helpers

def get_fernet(passphrase: str) -> Fernet:
    # Derive a 32-byte key from the passphrase (pad/truncate for demo; use PBKDF2 in prod)
    key = base64.urlsafe_b64encode((passphrase * 32)[:32].encode())
    return Fernet(key)

def encrypt_value(value: str, passphrase: str) -> str:
    f = get_fernet(passphrase)
    return f.encrypt(value.encode()).decode()

def decrypt_value(token: str, passphrase: str) -> str:
    f = get_fernet(passphrase)
    return f.decrypt(token.encode()).decode()

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SystemConfig(models.Model):
    debug = models.BooleanField(default=False)  # type: ignore[attr-defined]
    download_path = models.CharField(max_length=512)
    should_download_drm_content = models.BooleanField(default=False)  # type: ignore[attr-defined]

    ffmpeg_available = models.BooleanField(default=False)  # type: ignore[attr-defined]
    ffmpeg_path = models.CharField(max_length=512, blank=True, null=True)
    bento4_available = models.BooleanField(default=False)  # type: ignore[attr-defined]
    bento4_path = models.CharField(max_length=512, blank=True, null=True)  # mp4decrypt
    aria2c_available = models.BooleanField(default=False)  # type: ignore[attr-defined]
    aria2c_path = models.CharField(max_length=512, blank=True, null=True)
    geckodriver_available = models.BooleanField(default=False)  # type: ignore[attr-defined]
    geckodriver_path = models.CharField(max_length=512, blank=True, null=True)
    chromedriver_available = models.BooleanField(default=False)  # type: ignore[attr-defined]
    chromedriver_path = models.CharField(max_length=512, blank=True, null=True)
    mkvtoolnix_available = models.BooleanField(default=False)  # type: ignore[attr-defined]
    mkvtoolnix_path = models.CharField(max_length=512, blank=True, null=True)
    rclone_available = models.BooleanField(default=False)  # type: ignore[attr-defined]
    rclone_path = models.CharField(max_length=512, blank=True, null=True)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)  # type: ignore[attr-defined]
        obj.auto_detect_tools()
        return obj

    @staticmethod
    def get_jwt_secret_key():
        key = os.environ.get('JWT_SECRET_KEY')
        if not key:
            raise RuntimeError('JWT_SECRET_KEY must be set in the environment (.env)')
        return key

    def auto_detect_tools(self):
        ffmpeg_path = shutil.which('ffmpeg')
        self.ffmpeg_available = bool(ffmpeg_path)
        self.ffmpeg_path = ffmpeg_path or ''

        bento4_path = shutil.which('mp4decrypt')
        self.bento4_available = bool(bento4_path)
        self.bento4_path = bento4_path or ''

        aria2c_path = shutil.which('aria2c')
        self.aria2c_available = bool(aria2c_path)
        self.aria2c_path = aria2c_path or ''

        firefox_path = shutil.which('firefox')
        geckodriver_path = shutil.which('geckodriver') if firefox_path else None
        self.geckodriver_available = bool(geckodriver_path)
        self.geckodriver_path = geckodriver_path or ''

        chrome_path = shutil.which('chrome') or shutil.which('google-chrome')
        chromedriver_path = shutil.which('chromedriver') if chrome_path else None
        self.chromedriver_available = bool(chromedriver_path)
        self.chromedriver_path = chromedriver_path or ''

        mkvtoolnix_path = shutil.which('mkvmerge')
        self.mkvtoolnix_available = bool(mkvtoolnix_path)
        self.mkvtoolnix_path = mkvtoolnix_path or ''

        rclone_path = shutil.which('rclone')
        self.rclone_available = bool(rclone_path)
        self.rclone_path = rclone_path or ''
        # should_download_drm_content can only be True if bento4 is available
        if self.should_download_drm_content and not self.bento4_available:
            self.should_download_drm_content = False
        self.save()

    def save(self, *args, **kwargs):
        self.auto_detect_tools()
        super().save(*args, **kwargs)

    @classmethod
    def ensure_integrity(cls):
        obj = cls.get_solo()
        required_fields = [
            'download_path', 'debug', 'should_download_drm_content',
        ]
        missing = []
        for field in required_fields:
            value = getattr(obj, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(field)
        if missing:
            raise RuntimeError(f'Database integrity error: SystemConfig fields missing or empty: {", ".join(missing)}')
        # JWT_SECRET_KEY must be set in env
        _ = cls.get_jwt_secret_key()

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="platform_auths", null=True, blank=True)
    platform = models.ForeignKey('Platform', on_delete=models.CASCADE, related_name="auths")
    username = models.CharField(max_length=256)
    password_encrypted = models.TextField(null=True, blank=True)  # Encrypted at runtime
    token_encrypted = models.TextField(null=True, blank=True)  # Encrypted at runtime
    session_cookie_encrypted = models.TextField(null=True, blank=True)  # Encrypted at runtime
    token_type = models.CharField(max_length=32, null=True, blank=True)
    state = models.JSONField(default=dict, blank=True)
    refresh_token_encrypted = models.TextField(null=True, blank=True)  # Encrypted at runtime
    expires_at = models.DateTimeField(null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

    def set_credentials(self, password, token=None, session_cookie=None, refresh_token=None, passphrase=None):
        if not passphrase:
            raise ValueError('Passphrase required for encryption')
        self.password_encrypted = encrypt_value(password, passphrase)
        if token:
            self.token_encrypted = encrypt_value(token, passphrase)
        if session_cookie:
            self.session_cookie_encrypted = encrypt_value(session_cookie, passphrase)
        if refresh_token:
            self.refresh_token_encrypted = encrypt_value(refresh_token, passphrase)

    def get_credentials(self, passphrase):
        creds = {}
        try:
            creds['password'] = decrypt_value(str(self.password_encrypted), passphrase)
        except Exception:
            creds['password'] = None
        try:
            creds['token'] = decrypt_value(str(self.token_encrypted), passphrase) if self.token_encrypted else None
        except Exception:
            creds['token'] = None
        try:
            creds['session_cookie'] = decrypt_value(str(self.session_cookie_encrypted), passphrase) if self.session_cookie_encrypted else None
        except Exception:
            creds['session_cookie'] = None
        try:
            creds['refresh_token'] = decrypt_value(str(self.refresh_token_encrypted), passphrase) if self.refresh_token_encrypted else None
        except Exception:
            creds['refresh_token'] = None
        return creds

class Course(TimestampMixin):
    internal_id = models.AutoField(primary_key=True)
    katomart_id = models.UUIDField(null=True, blank=True, default=None)
    external_id = models.CharField(max_length=128, null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    formatted_name = models.CharField(max_length=128, null=True, blank=True)
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
    platform = models.ForeignKey('Platform', on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")
    auth = models.ForeignKey(PlatformAuth, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")

class Module(TimestampMixin):
    internal_id = models.AutoField(primary_key=True)
    katomart_id = models.UUIDField(null=True, blank=True, default=None)
    external_id = models.CharField(max_length=128, null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    formatted_name = models.CharField(max_length=128, null=True, blank=True)
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
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="modules", null=True, blank=True)

class Lesson(TimestampMixin):
    internal_id = models.AutoField(primary_key=True)
    katomart_id = models.UUIDField(null=True, blank=True, default=None)
    external_id = models.CharField(max_length=128, null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    formatted_name = models.CharField(max_length=128, null=True, blank=True)
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
    formatted_name = models.CharField(max_length=128, null=True, blank=True)
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

class UserFormattedName(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='formatted_names')
    content_type = models.CharField(max_length=32)  # 'course', 'module', 'lesson', 'file'
    object_id = models.IntegerField()
    formatted_name = models.CharField(max_length=128)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

class UserConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_config')
    download_path = models.CharField(max_length=512, null=True, blank=True)
    ffmpeg_path = models.CharField(max_length=512, blank=True, null=True)
    bento4_path = models.CharField(max_length=512, blank=True, null=True)
    aria2c_path = models.CharField(max_length=512, blank=True, null=True)
    geckodriver_path = models.CharField(max_length=512, blank=True, null=True)
    chromedriver_path = models.CharField(max_length=512, blank=True, null=True)
    mkvtoolnix_path = models.CharField(max_length=512, blank=True, null=True)
    rclone_path = models.CharField(max_length=512, blank=True, null=True)

    def get_download_path(self):
        if self.download_path:
            return Path(str(self.download_path))
        return None

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

MAX_PATH = 260
MAX_COURSE_NAME = 64
MAX_MODULE_NAME = 64
MAX_LESSON_NAME = 64
MAX_FILE_NAME = 80

# Reserved Windows names and illegal character regex from old utils
_INVALID_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1F\x7F]')
_RESERVED_WIN_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    *(f'COM{i}' for i in range(1, 10)),
    *(f'LPT{i}' for i in range(1, 10)),
}

def _sanitize_raw_text(text: str) -> str:
    sanitized = _INVALID_CHARS_RE.sub('', text)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    sanitized = sanitized.rstrip('. ')
    return sanitized

def _avoid_reserved_names(name: str) -> str:
    if name.upper() in _RESERVED_WIN_NAMES:
        return name + '_k'
    return name

def _truncate_text(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    if max_len < 3:
        return text[:max_len]
    ellipsis = "…"
    return text[:max_len - len(ellipsis)] + ellipsis

def sanitize_and_truncate_path_component(
        original_name: str,
        max_len: int,
        is_filename: bool = False,
        prefix: str = "",
        suffix: str = ""
) -> str:
    if max_len <= len(prefix) + len(suffix) + 1:
        placeholder = "default_k"
        if is_filename:
            placeholder = f"file_k{suffix}"
        combined = f"{prefix}{placeholder}"
        if len(combined) > max_len:
            if is_filename and max_len > len(suffix):
                return combined[:max_len - len(suffix)] + suffix
            return combined[:max_len]
        return combined
    available_len_for_name = max_len - len(prefix) - len(suffix)
    sanitized_name = _sanitize_raw_text(original_name)
    sanitized_name = _avoid_reserved_names(sanitized_name)
    if not sanitized_name:
        sanitized_name = "untitled" if is_filename else "unnamed_folder"
    truncated_name = _truncate_text(sanitized_name, available_len_for_name)
    return f"{prefix}{truncated_name}{suffix}"

def get_user_download_path(user):
    if user.is_authenticated:
        user_config = getattr(user, 'user_config', None)
        if user_config and user_config.download_path:
            return Path(str(user_config.download_path))
    # fallback to global config
    config = SystemConfig.get_solo()
    base_path = config.download_path
    if not base_path:
        raise RuntimeError('Global config.download_path must be set!')
    base_path = str(base_path)
    if not os.path.isabs(base_path):
        base_path = str(Path(Path(__file__).resolve().parent.parent, base_path))
    return Path(base_path)

def ensure_directory_exists(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    return directory

def remaining_path_length(path: Path) -> int:
    max_length = 260
    current_length = len(str(path.resolve()))
    return max_length - current_length

def build_user_path(user, course, module, lesson, file, order_dict=None):
    if order_dict is None:
        order_dict = {}
    # Get base download path
    base_path = get_user_download_path(user)
    ensure_directory_exists(base_path)
    # Order prefix: always 3 digits, zero-padded, with '. '
    def order_prefix(obj):
        order = getattr(obj, 'order', None)
        if order is None:
            return '000. '
        return f"{int(order):03d}. "
    # Name logic
    def get_name(obj, content_type, is_filename=False):
        if user.is_authenticated:
            uf = UserFormattedName.objects.filter(user=user, content_type=content_type, object_id=obj.internal_id).first()  # type: ignore[attr-defined]
            if uf:
                return uf.formatted_name
        return getattr(obj, 'formatted_name', '') or getattr(obj, 'name', '')
    # Max lengths
    MAX_COURSE_NAME = 64
    MAX_MODULE_NAME = 64
    MAX_LESSON_NAME = 64
    MAX_FILE_NAME = 80
    # Compose each segment
    course_name = sanitize_and_truncate_path_component(
        get_name(course, 'course'), MAX_COURSE_NAME, False, order_prefix(course))
    module_name = sanitize_and_truncate_path_component(
        get_name(module, 'module'), MAX_MODULE_NAME, False, order_prefix(module))
    lesson_name = sanitize_and_truncate_path_component(
        get_name(lesson, 'lesson'), MAX_LESSON_NAME, False, order_prefix(lesson))
    ext = getattr(file, 'file_type', '')
    file_name = sanitize_and_truncate_path_component(
        get_name(file, 'file', True), MAX_FILE_NAME, True, order_prefix(file), f'.{ext}' if ext else '')
    # Build path
    path = base_path / course_name / module_name / lesson_name / file_name
    # Ensure path length
    if remaining_path_length(path) < 0:
        # Truncate file_name further if needed
        excess = abs(remaining_path_length(path))
        file_name = file_name[:-excess]
        path = base_path / course_name / module_name / lesson_name / file_name
    return path
