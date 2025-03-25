from django.apps import AppConfig
import threading


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from .tasks import start_scheduler

        # Prevent multiple scheduler instances when using Django's auto-reloader
        if not hasattr(self, '_scheduler_started'):
            self._scheduler_started = True
            threading.Thread(target=start_scheduler, daemon=True).start()