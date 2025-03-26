from django.apps import AppConfig


class TermSheetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'term_sheet'

    def ready(self):
        import term_sheet.signals # type: ignore