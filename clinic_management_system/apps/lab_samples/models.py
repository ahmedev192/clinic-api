from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.lab_requests.models import LabRequestItem


class Sample(models.Model):
    """Sample collection and tracking"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending Collection')),
        ('collected', _('Collected')),
        ('in_analysis', _('In Analysis')),
        ('completed', _('Analysis Completed')),
        ('rejected', _('Rejected')),
        ('expired', _('Expired')),
    ]
    
    SAMPLE_TYPES = [
        ('blood', _('Blood')),
        ('urine', _('Urine')),
        ('stool', _('Stool')),
        ('sputum', _('Sputum')),
        ('tissue', _('Tissue')),
        ('other', _('Other')),
    ]
    
    # Sample identification
    barcode = models.CharField(max_length=100, unique=True, verbose_name=_("Barcode"))
    tracking_code = models.CharField(max_length=50, unique=True, verbose_name=_("Tracking Code"))
    
    # Related request item
    request_item = models.OneToOneField(
        LabRequestItem, 
        on_delete=models.CASCADE, 
        related_name='sample',
        verbose_name=_("Request Item")
    )
    
    # Sample details
    sample_type = models.CharField(max_length=20, choices=SAMPLE_TYPES, verbose_name=_("Sample Type"))
    volume = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name=_("Volume (ml)")
    )
    container_type = models.CharField(max_length=100, blank=True, verbose_name=_("Container Type"))
    
    # Collection information
    collection_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Collection Date"))
    collector_name = models.CharField(max_length=200, blank=True, verbose_name=_("Collector Name"))
    collector_name_ar = models.CharField(max_length=200, blank=True, verbose_name=_("Collector Name (Arabic)"))
    collection_location = models.CharField(max_length=200, blank=True, verbose_name=_("Collection Location"))
    
    # Sample status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    storage_location = models.CharField(max_length=200, blank=True, verbose_name=_("Storage Location"))
    temperature = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name=_("Storage Temperature (°C)")
    )
    
    # Notes and comments
    collection_notes_en = models.TextField(blank=True, verbose_name=_("Collection Notes (English)"))
    collection_notes_ar = models.TextField(blank=True, verbose_name=_("Collection Notes (Arabic)"))
    rejection_reason_en = models.TextField(blank=True, verbose_name=_("Rejection Reason (English)"))
    rejection_reason_ar = models.TextField(blank=True, verbose_name=_("Rejection Reason (Arabic)"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Expiry Date"))
    
    # Metadata
    created_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Created By")
    )
    
    class Meta:
        verbose_name = _("Sample")
        verbose_name_plural = _("Samples")
        ordering = ['-created_at']

    def __str__(self):
        return f"Sample {self.barcode} - {self.request_item.test.name_en}"

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = self.generate_barcode()
        if not self.tracking_code:
            self.tracking_code = self.generate_tracking_code()
        super().save(*args, **kwargs)

    def generate_barcode(self):
        """Generate unique barcode for sample"""
        import random
        import string
        
        # Format: S + 8 random alphanumeric characters
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"S{random_chars}"

    def generate_tracking_code(self):
        """Generate unique tracking code for sample"""
        from datetime import datetime
        
        # Format: TC + YYYYMMDD + 4 random digits
        date_str = datetime.now().strftime('%Y%m%d')
        import random
        random_suffix = random.randint(1000, 9999)
        return f"TC{date_str}{random_suffix}"

    @property
    def is_expired(self):
        """Check if sample has expired"""
        if not self.expiry_date:
            return False
        from django.utils import timezone
        return timezone.now() > self.expiry_date

    @property
    def days_until_expiry(self):
        """Calculate days until sample expires"""
        if not self.expiry_date:
            return None
        from django.utils import timezone
        delta = self.expiry_date - timezone.now()
        return delta.days


class SampleCollection(models.Model):
    """Batch collection of samples"""
    
    collection_batch_id = models.CharField(max_length=50, unique=True, verbose_name=_("Batch ID"))
    collection_date = models.DateTimeField(verbose_name=_("Collection Date"))
    collector_name = models.CharField(max_length=200, verbose_name=_("Collector Name"))
    collector_name_ar = models.CharField(max_length=200, verbose_name=_("Collector Name (Arabic)"))
    location = models.CharField(max_length=200, verbose_name=_("Collection Location"))
    
    # Batch details
    total_samples = models.PositiveIntegerField(verbose_name=_("Total Samples"))
    collected_samples = models.PositiveIntegerField(default=0, verbose_name=_("Collected Samples"))
    
    # Notes
    notes_en = models.TextField(blank=True, verbose_name=_("Notes (English)"))
    notes_ar = models.TextField(blank=True, verbose_name=_("Notes (Arabic)"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = _("Sample Collection")
        verbose_name_plural = _("Sample Collections")
        ordering = ['-collection_date']

    def __str__(self):
        return f"Collection Batch {self.collection_batch_id} - {self.collection_date.date()}"

    def save(self, *args, **kwargs):
        if not self.collection_batch_id:
            self.collection_batch_id = self.generate_batch_id()
        super().save(*args, **kwargs)

    def generate_batch_id(self):
        """Generate unique batch ID"""
        from datetime import datetime
        import random
        
        # Format: CB + YYYYMMDD + 3 random digits
        date_str = datetime.now().strftime('%Y%m%d')
        random_suffix = random.randint(100, 999)
        return f"CB{date_str}{random_suffix}"

