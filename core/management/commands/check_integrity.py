from django.core.management.base import BaseCommand
from core.models import SystemConfig, PlatformAuth
from django.contrib.auth import get_user_model
import os
from pathlib import Path
from django.db import models

class Command(BaseCommand):
    help = 'Check system configuration and tool integrity, and ensure admin account if .env is present.'

    def handle(self, *args, **options):
        # --- Database integrity check ---
        config = SystemConfig.get_solo()
        required_fields = [
            'download_path',
            'debug',
            'should_download_drm_content',
        ]
        missing = []
        for field in required_fields:
            value = getattr(config, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(field)
        if missing:
            raise RuntimeError(f'Database integrity error: SystemConfig fields missing or empty: {", ".join(missing)}')
        # JWT_SECRET_KEY must be set in env
        _ = SystemConfig.get_jwt_secret_key()
        # --- DRM content sanity check ---
        if config.should_download_drm_content and (not config.bento4_path or not str(config.bento4_path).strip()):
            raise RuntimeError('Sanity check failed: should_download_drm_content is True but bento4_path is not set!')
        self.stdout.write(self.style.SUCCESS('System configuration integrity check passed.'))  # type: ignore[attr-defined]

        # --- Optional: Ensure admin account from .env ---
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        env_path = Path(os.environ.get('BASE_DIR', '.')) / '.env'
        su_created = False
        if username and password:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, password=password)
                su_created = True
            if su_created and env_path.exists():
                with env_path.open('r', encoding='utf-8') as f:
                    lines = f.readlines()
                with env_path.open('w', encoding='utf-8') as f:
                    for line in lines:
                        if not (line.strip().startswith('DJANGO_SUPERUSER_USERNAME=') or line.strip().startswith('DJANGO_SUPERUSER_PASSWORD=')):
                            f.write(line)
        if su_created:
            self.stdout.write(self.style.SUCCESS('Admin account created from .env and credentials removed.'))  # type: ignore[attr-defined]

        # --- PlatformAuth integrity check ---
        invalid_auths = PlatformAuth.objects.filter(models.Q(password_encrypted__isnull=True) | models.Q(password_encrypted=''))  # type: ignore[attr-defined]
        if invalid_auths.exists():
            raise RuntimeError(f'PlatformAuth integrity error: {invalid_auths.count()} entries missing password_encrypted.')
