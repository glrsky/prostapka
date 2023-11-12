from django.apps import AppConfig

class EspressoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'espresso'

    def ready(self):
        import espresso.signals

