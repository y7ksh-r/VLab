from django.apps import AppConfig


class LabAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lab_app'
    
    def ready(self):
        import lab_app.signals
