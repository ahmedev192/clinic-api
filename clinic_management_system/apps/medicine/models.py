from django.db import models
from apps.accounts.models import User
from django.utils import timezone


class Category(models.Model):
    """Medicine category model with multilingual support"""
    name_en = models.CharField(max_length=100, verbose_name="Category Name (English)")
    name_ar = models.CharField(max_length=100, verbose_name="Category Name (Arabic)")
    description_en = models.TextField(blank=True, null=True, verbose_name="Description (English)")
    description_ar = models.TextField(blank=True, null=True, verbose_name="Description (Arabic)")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_categories')
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_categories')

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name_en']

    def __str__(self):
        return f"{self.name_en} / {self.name_ar}"


class Medicine(models.Model):
    """Medicine model with comprehensive multilingual support"""
    
    DOSAGE_FORMS = [
        ('tablet', 'Tablet'),
        ('syrup', 'Syrup'),
        ('capsule', 'Capsule'),
        ('injection', 'Injection'),
        ('cream', 'Cream'),
        ('ointment', 'Ointment'),
        ('drops', 'Drops'),
        ('inhaler', 'Inhaler'),
        ('patch', 'Patch'),
        ('suppository', 'Suppository'),
        ('other', 'Other'),
    ]

    UNITS = [
        ('box', 'Box'),
        ('bottle', 'Bottle'),
        ('pack', 'Pack'),
        ('vial', 'Vial'),
        ('tube', 'Tube'),
        ('strip', 'Strip'),
        ('piece', 'Piece'),
        ('ml', 'Milliliter'),
        ('mg', 'Milligram'),
        ('g', 'Gram'),
        ('other', 'Other'),
    ]

    # Unique internal code for tracking
    internal_code = models.CharField(max_length=50, unique=True, verbose_name="Internal Code")
    
    # Basic information
    name_en = models.CharField(max_length=200, verbose_name="Medicine Name (English)")
    name_ar = models.CharField(max_length=200, verbose_name="Medicine Name (Arabic)")
    
    # Names
    generic_name_en = models.CharField(max_length=200, verbose_name="Generic Name (English)")
    generic_name_ar = models.CharField(max_length=200, verbose_name="Generic Name (Arabic)")
    brand_name_en = models.CharField(max_length=200, verbose_name="Brand Name (English)")
    brand_name_ar = models.CharField(max_length=200, verbose_name="Brand Name (Arabic)")
    
    # Classification
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Category")
    dosage_form = models.CharField(max_length=20, choices=DOSAGE_FORMS, verbose_name="Dosage Form")
    strength = models.CharField(max_length=100, verbose_name="Strength (e.g., 500mg, 250ml)")
    unit = models.CharField(max_length=20, choices=UNITS, verbose_name="Unit")
    
    # Inventory management
    reorder_level = models.PositiveIntegerField(default=10, verbose_name="Reorder Level")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_archived = models.BooleanField(default=False, verbose_name="Archived")
    
    # Multilingual notes and instructions
    notes_en = models.TextField(blank=True, null=True, verbose_name="Notes (English)")
    notes_ar = models.TextField(blank=True, null=True, verbose_name="Notes (Arabic)")
    usage_instructions_en = models.TextField(blank=True, null=True, verbose_name="Usage Instructions (English)")
    usage_instructions_ar = models.TextField(blank=True, null=True, verbose_name="Usage Instructions (Arabic)")
    
    # Pricing (optional, can be overridden in stock records)
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Base Cost")
    base_selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Base Selling Price")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_medicines')
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_medicines')

    class Meta:
        verbose_name = "Medicine"
        verbose_name_plural = "Medicines"
        ordering = ['name_en']
        indexes = [
            models.Index(fields=['internal_code']),
            models.Index(fields=['name_en']),
            models.Index(fields=['name_ar']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active', 'is_archived']),
        ]

    def __str__(self):
        return f"{self.name_en} / {self.name_ar} ({self.internal_code})"

    def get_current_stock(self):
        """Get current total stock quantity"""
        from apps.stock.models import Stock
        return Stock.objects.filter(medicine=self, is_active=True).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    def is_low_stock(self):
        """Check if medicine is below reorder level"""
        return self.get_current_stock() <= self.reorder_level

    def get_expiring_soon(self, days=30):
        """Get stock items expiring within specified days"""
        from apps.stock.models import Stock
        from django.utils import timezone
        from datetime import timedelta
        
        future_date = timezone.now().date() + timedelta(days=days)
        return Stock.objects.filter(
            medicine=self,
            is_active=True,
            expiration_date__lte=future_date,
            expiration_date__gte=timezone.now().date()
        )

    def get_expired(self):
        """Get expired stock items"""
        from apps.stock.models import Stock
        from django.utils import timezone
        
        return Stock.objects.filter(
            medicine=self,
            is_active=True,
            expiration_date__lt=timezone.now().date()
        )


