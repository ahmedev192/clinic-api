from django.db import models
from django.utils.translation import gettext_lazy as _
from modeltranslation.translator import translator, TranslationOptions


class TestCategory(models.Model):
    """Categories for lab tests (e.g., Blood, Urine, Imaging)"""
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Test Category")
        verbose_name_plural = _("Test Categories")
        ordering = ['name']

    def __str__(self):
        return self.name


class LabTest(models.Model):
    """Lab test catalog with multilingual support"""
    name = models.CharField(max_length=200, verbose_name=_("Test Name"))
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE, related_name='tests')
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Test Code"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    
    # Normal range / reference values
    normal_range = models.TextField(blank=True, verbose_name=_("Normal Range"))
    
    # Description and preparation instructions
    description = models.TextField(blank=True, verbose_name=_("Description"))
    preparation_instructions = models.TextField(blank=True, verbose_name=_("Preparation Instructions"))
    
    # Test specifications
    unit = models.CharField(max_length=50, blank=True, verbose_name=_("Unit of Measurement"))
    sample_type = models.CharField(max_length=100, blank=True, verbose_name=_("Sample Type"))
    processing_time_hours = models.PositiveIntegerField(default=24, verbose_name=_("Processing Time (Hours)"))
    
    # Status and metadata
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("Lab Test")
        verbose_name_plural = _("Lab Tests")
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def current_name(self):
        """Return name based on current language"""
        from django.utils import translation
        if translation.get_language() == 'ar':
            return getattr(self, 'name_ar', self.name)
        return getattr(self, 'name_en', self.name)

    @property
    def current_description(self):
        """Return description based on current language"""
        from django.utils import translation
        if translation.get_language() == 'ar':
            return getattr(self, 'description_ar', self.description)
        return getattr(self, 'description_en', self.description)


class TestCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


class TestTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'normal_range', 'preparation_instructions')


# Translation registration moved to apps.py ready() method

