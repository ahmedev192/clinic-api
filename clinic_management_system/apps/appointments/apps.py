from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.appointments'
    verbose_name = 'Appointments & Scheduling'
    
    def ready(self):
        """Import signals when the app is ready."""
        import apps.appointments.signals