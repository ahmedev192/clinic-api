from django.db import models
from django.utils.translation import gettext_lazy as _
from modeltranslation.translator import translator, TranslationOptions


class TestCategory(models.Model):
    """Categories for lab tests (e.g., Blood, Urine, Imaging)"""
    name_en = models.CharField(max_length=100, verbose_name=_("Name (English)"))
    name_ar = models.CharField(max_length=100, verbose_name=_("Name (Arabic)"))
    description_en = models.TextField(blank=True, verbose_name=_("Description (English)"))
    description_ar = models.TextField(blank=True, verbose_name=_("Description (Arabic)"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Test Category")
        verbose_name_plural = _("Test Categories")
        ordering = ['name_en']

    def __str__(self):
        return f"{self.name_en} / {self.name_ar}"


class LabTest(models.Model):
    """Lab test catalog with multilingual support"""
    name_en = models.CharField(max_length=200, verbose_name=_("Test Name (English)"))
    name_ar = models.CharField(max_length=200, verbose_name=_("Test Name (Arabic)"))
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE, related_name='tests')
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Test Code"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    
    # Normal range / reference values
    normal_range_en = models.TextField(blank=True, verbose_name=_("Normal Range (English)"))
    normal_range_ar = models.TextField(blank=True, verbose_name=_("Normal Range (Arabic)"))
    
    # Description and preparation instructions
    description_en = models.TextField(blank=True, verbose_name=_("Description (English)"))
    description_ar = models.TextField(blank=True, verbose_name=_("Description (Arabic)"))
    preparation_instructions_en = models.TextField(blank=True, verbose_name=_("Preparation Instructions (English)"))
    preparation_instructions_ar = models.TextField(blank=True, verbose_name=_("Preparation Instructions (Arabic)"))
    
    # Test specifications
    unit = models.CharField(max_length=50, blank=True, verbose_name=_("Unit of Measurement"))
    sample_type = models.CharField(max_length=100, blank=True, verbose_name=_("Sample Type"))
    processing_time_hours = models.PositiveIntegerField(default=24, verbose_name=_("Processing Time (Hours)"))
    
    # Status and metadata
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("Lab Test")
        verbose_name_plural = _("Lab Tests")
        ordering = ['category', 'name_en']

    def __str__(self):
        return f"{self.name_en} ({self.code})"

    @property
    def current_name(self):
        """Return name based on current language"""
        from django.utils import translation
        if translation.get_language() == 'ar':
            return self.name_ar
        return self.name_en

    @property
    def current_description(self):
        """Return description based on current language"""
        from django.utils import translation
        if translation.get_language() == 'ar':
            return self.description_ar
        return self.description_en


class TestTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'normal_range', 'preparation_instructions')


translator.register(LabTest, TestTranslationOptions)
