from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model
import os
from pathlib import Path


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # type: ignore
    name = 'core'

    def ready(self):
        from django.db.utils import OperationalError
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        env_path = Path(settings.BASE_DIR) / '.env'
        su_created = False
        try:
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
        except OperationalError:
            # Database might not be migrated yet
            pass
