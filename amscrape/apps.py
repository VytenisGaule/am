from django.apps import AppConfig


class AmscrapeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'amscrape'

    def ready(self):
        import amscrape.signals
