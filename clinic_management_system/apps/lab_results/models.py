from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.lab_samples.models import Sample


class LabResult(models.Model):
    """Lab test results with approval workflow"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('preliminary', _('Preliminary')),
        ('final', _('Final')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    ]
    
    ABNORMALITY_CHOICES = [
        ('normal', _('Normal')),
        ('high', _('High')),
        ('low', _('Low')),
        ('critical_high', _('Critical High')),
        ('critical_low', _('Critical Low')),
        ('abnormal', _('Abnormal')),
    ]
    
    # Related sample and test
    sample = models.OneToOneField(
        Sample, 
        on_delete=models.CASCADE, 
        related_name='result',
        verbose_name=_("Sample")
    )
    
    # Result values
    measured_value = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True,
        verbose_name=_("Measured Value")
    )
    unit = models.CharField(max_length=50, blank=True, verbose_name=_("Unit"))
    
    # Reference ranges
    normal_range_min = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True,
        verbose_name=_("Normal Range (Min)")
    )
    normal_range_max = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True,
        verbose_name=_("Normal Range (Max)")
    )
    normal_range_text_en = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name=_("Normal Range Text (English)")
    )
    normal_range_text_ar = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name=_("Normal Range Text (Arabic)")
    )
    
    # Result interpretation
    abnormality_flag = models.CharField(
        max_length=20, 
        choices=ABNORMALITY_CHOICES, 
        default='normal',
        verbose_name=_("Abnormality Flag")
    )
    is_critical = models.BooleanField(default=False, verbose_name=_("Critical Result"))
    
    # Comments and notes
    comments_en = models.TextField(blank=True, verbose_name=_("Comments (English)"))
    comments_ar = models.TextField(blank=True, verbose_name=_("Comments (Arabic)"))
    interpretation_en = models.TextField(blank=True, verbose_name=_("Interpretation (English)"))
    interpretation_ar = models.TextField(blank=True, verbose_name=_("Interpretation (Arabic)"))
    
    # Status and approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    is_approved = models.BooleanField(default=False, verbose_name=_("Approved"))
    approved_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_results',
        verbose_name=_("Approved By")
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))
    
    # Rejection details
    rejection_reason_en = models.TextField(blank=True, verbose_name=_("Rejection Reason (English)"))
    rejection_reason_ar = models.TextField(blank=True, verbose_name=_("Rejection Reason (Arabic)"))
    rejected_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='rejected_results',
        verbose_name=_("Rejected By")
    )
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Rejected At"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))
    
    # Metadata
    created_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_results',
        verbose_name=_("Created By")
    )
    
    class Meta:
        verbose_name = _("Lab Result")
        verbose_name_plural = _("Lab Results")
        ordering = ['-created_at']

    def __str__(self):
        return f"Result for {self.sample.barcode} - {self.sample.request_item.test.name_en}"

    def save(self, *args, **kwargs):
        # Auto-calculate abnormality flag based on measured value and normal range
        if self.measured_value and self.normal_range_min and self.normal_range_max:
            self.abnormality_flag = self.calculate_abnormality_flag()
        
        # Set critical flag for critical abnormalities
        if self.abnormality_flag in ['critical_high', 'critical_low']:
            self.is_critical = True
        
        super().save(*args, **kwargs)

    def calculate_abnormality_flag(self):
        """Calculate abnormality flag based on measured value and normal range"""
        if not self.measured_value or not self.normal_range_min or not self.normal_range_max:
            return 'normal'
        
        value = float(self.measured_value)
        min_val = float(self.normal_range_min)
        max_val = float(self.normal_range_max)
        
        if value < min_val:
            # Check if it's critically low (more than 50% below normal)
            if value < (min_val * 0.5):
                return 'critical_low'
            return 'low'
        elif value > max_val:
            # Check if it's critically high (more than 200% above normal)
            if value > (max_val * 2):
                return 'critical_high'
            return 'high'
        else:
            return 'normal'

    @property
    def is_abnormal(self):
        """Check if result is abnormal"""
        return self.abnormality_flag != 'normal'

    @property
    def status_display(self):
        """Get human-readable status"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def abnormality_display(self):
        """Get human-readable abnormality flag"""
        return dict(self.ABNORMALITY_CHOICES).get(self.abnormality_flag, self.abnormality_flag)


class ResultAttachment(models.Model):
    """File attachments for lab results (images, documents, etc.)"""
    
    result = models.ForeignKey(
        LabResult, 
        on_delete=models.CASCADE, 
        related_name='attachments',
        verbose_name=_("Lab Result")
    )
    
    file = models.FileField(upload_to='lab_results/attachments/', verbose_name=_("File"))
    file_name = models.CharField(max_length=255, verbose_name=_("File Name"))
    file_type = models.CharField(max_length=100, verbose_name=_("File Type"))
    file_size = models.PositiveIntegerField(verbose_name=_("File Size (bytes)"))
    
    description_en = models.CharField(max_length=500, blank=True, verbose_name=_("Description (English)"))
    description_ar = models.CharField(max_length=500, blank=True, verbose_name=_("Description (Arabic)"))
    
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = _("Result Attachment")
        verbose_name_plural = _("Result Attachments")
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Attachment for {self.result.sample.barcode} - {self.file_name}"

    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = self.file.name
        if not self.file_type:
            self.file_type = self.file.name.split('.')[-1].lower()
        if not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

