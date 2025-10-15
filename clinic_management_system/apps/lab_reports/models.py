from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.lab_requests.models import LabRequest


class LabReport(models.Model):
    """Generated lab reports for patients"""
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('generated', _('Generated')),
        ('delivered', _('Delivered')),
        ('archived', _('Archived')),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', _('PDF')),
        ('html', _('HTML')),
        ('json', _('JSON')),
    ]
    
    # Report identification
    report_number = models.CharField(max_length=50, unique=True, verbose_name=_("Report Number"))
    
    # Related lab request
    lab_request = models.ForeignKey(
        LabRequest, 
        on_delete=models.CASCADE, 
        related_name='reports',
        verbose_name=_("Lab Request")
    )
    
    # Report details
    title_en = models.CharField(max_length=200, verbose_name=_("Report Title (English)"))
    title_ar = models.CharField(max_length=200, verbose_name=_("Report Title (Arabic)"))
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf', verbose_name=_("Format"))
    
    # Report content (stored as JSON for flexibility)
    content_en = models.JSONField(verbose_name=_("Report Content (English)"))
    content_ar = models.JSONField(verbose_name=_("Report Content (Arabic)"))
    
    # File storage
    file_path = models.CharField(max_length=500, blank=True, verbose_name=_("File Path"))
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("File Size (bytes)"))
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_("Status"))
    is_public = models.BooleanField(default=False, verbose_name=_("Public Access"))
    
    # Timestamps
    generated_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Generated At"))
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Delivered At"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    # Metadata
    created_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Created By")
    )
    
    class Meta:
        verbose_name = _("Lab Report")
        verbose_name_plural = _("Lab Reports")
        ordering = ['-created_at']

    def __str__(self):
        return f"Report {self.report_number} - {self.lab_request.request_number}"

    def save(self, *args, **kwargs):
        if not self.report_number:
            self.report_number = self.generate_report_number()
        super().save(*args, **kwargs)

    def generate_report_number(self):
        """Generate unique report number"""
        from datetime import datetime
        import random
        
        # Format: RPT + YYYYMMDD + 4 random digits
        date_str = datetime.now().strftime('%Y%m%d')
        random_suffix = random.randint(1000, 9999)
        return f"RPT{date_str}{random_suffix}"

    @property
    def current_title(self):
        """Return title based on current language"""
        from django.utils import translation
        if translation.get_language() == 'ar':
            return self.title_ar
        return self.title_en

    @property
    def current_content(self):
        """Return content based on current language"""
        from django.utils import translation
        if translation.get_language() == 'ar':
            return self.content_ar
        return self.content_en


class ReportTemplate(models.Model):
    """Templates for generating lab reports"""
    
    name_en = models.CharField(max_length=200, verbose_name=_("Template Name (English)"))
    name_ar = models.CharField(max_length=200, verbose_name=_("Template Name (Arabic)"))
    description_en = models.TextField(blank=True, verbose_name=_("Description (English)"))
    description_ar = models.TextField(blank=True, verbose_name=_("Description (Arabic)"))
    
    # Template content
    template_content_en = models.TextField(verbose_name=_("Template Content (English)"))
    template_content_ar = models.TextField(verbose_name=_("Template Content (Arabic)"))
    
    # Template settings
    is_default = models.BooleanField(default=False, verbose_name=_("Default Template"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_report_templates')
    
    class Meta:
        verbose_name = _("Report Template")
        verbose_name_plural = _("Report Templates")
        ordering = ['name_en']

    def __str__(self):
        return f"{self.name_en} / {self.name_ar}"

    def save(self, *args, **kwargs):
        # Ensure only one default template
        if self.is_default:
            ReportTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class ReportDelivery(models.Model):
    """Track report delivery to patients/doctors"""
    
    DELIVERY_METHOD_CHOICES = [
        ('email', _('Email')),
        ('sms', _('SMS')),
        ('portal', _('Patient Portal')),
        ('print', _('Print')),
        ('api', _('API Integration')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed')),
        ('opened', _('Opened')),
    ]
    
    # Related report
    report = models.ForeignKey(
        LabReport, 
        on_delete=models.CASCADE, 
        related_name='deliveries',
        verbose_name=_("Lab Report")
    )
    
    # Delivery details
    delivery_method = models.CharField(
        max_length=20, 
        choices=DELIVERY_METHOD_CHOICES, 
        verbose_name=_("Delivery Method")
    )
    recipient_email = models.EmailField(blank=True, verbose_name=_("Recipient Email"))
    recipient_phone = models.CharField(max_length=20, blank=True, verbose_name=_("Recipient Phone"))
    recipient_name = models.CharField(max_length=200, verbose_name=_("Recipient Name"))
    recipient_name_ar = models.CharField(max_length=200, verbose_name=_("Recipient Name (Arabic)"))
    
    # Delivery status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    delivery_reference = models.CharField(max_length=200, blank=True, verbose_name=_("Delivery Reference"))
    
    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Sent At"))
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Delivered At"))
    opened_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Opened At"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    
    # Error handling
    error_message = models.TextField(blank=True, verbose_name=_("Error Message"))
    retry_count = models.PositiveIntegerField(default=0, verbose_name=_("Retry Count"))
    
    class Meta:
        verbose_name = _("Report Delivery")
        verbose_name_plural = _("Report Deliveries")
        ordering = ['-created_at']

    def __str__(self):
        return f"Delivery {self.id} - {self.report.report_number} to {self.recipient_name}"
