from django.apps import AppConfig


class PatientManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.patient_management'
    
    def ready(self):
        import apps.patient_management.signals
