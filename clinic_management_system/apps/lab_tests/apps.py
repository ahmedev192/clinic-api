from django.apps import AppConfig


class LabTestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.lab_tests'
    verbose_name = 'Lab Tests'
    
    def ready(self):
        from .models import TestCategory, LabTest, TestCategoryTranslationOptions, TestTranslationOptions
        from modeltranslation.translator import translator
        
        translator.register(TestCategory, TestCategoryTranslationOptions)
        translator.register(LabTest, TestTranslationOptions)