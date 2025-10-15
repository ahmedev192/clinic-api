from django.apps import AppConfig


class StaffManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.staff_management'
    
    def ready(self):
        import apps.staff_management.signals
