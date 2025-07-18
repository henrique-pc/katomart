from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model
import os
from pathlib import Path


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # type: ignore
    name = 'core'

    def ready(self):
        # No database queries or integrity checks here per Django best practices.
        # All integrity checks should be run via a management command or at runtime, not at import/startup.
        pass
