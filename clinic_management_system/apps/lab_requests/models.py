from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.lab_tests.models import LabTest
from apps.patient_management.models import Patient
from apps.staff_management.models import Doctor


class LabRequest(models.Model):
    """Lab test requests from doctors"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('collected', _('Collected')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    URGENCY_CHOICES = [
        ('routine', _('Routine')),
        ('urgent', _('Urgent')),
        ('stat', _('STAT (Immediate)')),
    ]
    
    # Request identification
    request_number = models.CharField(max_length=50, unique=True, verbose_name=_("Request Number"))
    
    # Patient and doctor references
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name=_("Patient"))
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name=_("Doctor"))
    
    # Keep name fields for display purposes (can be removed later if not needed)
    patient_name = models.CharField(max_length=200, verbose_name=_("Patient Name"))
    patient_name_ar = models.CharField(max_length=200, verbose_name=_("Patient Name (Arabic)"))
    doctor_name = models.CharField(max_length=200, verbose_name=_("Doctor Name"))
    doctor_name_ar = models.CharField(max_length=200, verbose_name=_("Doctor Name (Arabic)"))
    
    # Clinical information
    clinical_notes_en = models.TextField(blank=True, verbose_name=_("Clinical Notes (English)"))
    clinical_notes_ar = models.TextField(blank=True, verbose_name=_("Clinical Notes (Arabic)"))
    diagnosis_en = models.TextField(blank=True, verbose_name=_("Diagnosis (English)"))
    diagnosis_ar = models.TextField(blank=True, verbose_name=_("Diagnosis (Arabic)"))
    
    # Request details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='routine', verbose_name=_("Urgency"))
    
    # Timestamps
    request_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Request Date"))
    collection_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Collection Date"))
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Completion Date"))
    
    # Metadata
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Created By"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        verbose_name = _("Lab Request")
        verbose_name_plural = _("Lab Requests")
        ordering = ['-request_date']

    def __str__(self):
        return f"Lab Request {self.request_number} - {self.patient_name}"

    def save(self, *args, **kwargs):
        if not self.request_number:
            self.request_number = self.generate_request_number()
        super().save(*args, **kwargs)

    def generate_request_number(self):
        """Generate unique request number"""
        from datetime import datetime
        import random
        
        # Format: LR + YYYYMMDD + 4 random digits
        date_str = datetime.now().strftime('%Y%m%d')
        random_suffix = random.randint(1000, 9999)
        return f"LR{date_str}{random_suffix}"


class LabRequestItem(models.Model):
    """Individual test items within a lab request"""
    
    request = models.ForeignKey(LabRequest, on_delete=models.CASCADE, related_name='items', verbose_name=_("Lab Request"))
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE, verbose_name=_("Lab Test"))
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name=_("Quantity"))
    
    # Test-specific notes
    notes_en = models.TextField(blank=True, verbose_name=_("Notes (English)"))
    notes_ar = models.TextField(blank=True, verbose_name=_("Notes (Arabic)"))
    
    # Status tracking
    is_collected = models.BooleanField(default=False, verbose_name=_("Collected"))
    is_completed = models.BooleanField(default=False, verbose_name=_("Completed"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Lab Request Item")
        verbose_name_plural = _("Lab Request Items")
        unique_together = ['request', 'test']
        ordering = ['test__category', 'test__name_en']

    def __str__(self):
        return f"{self.request.request_number} - {self.test.name_en}"

    @property
    def total_price(self):
        """Calculate total price for this item"""
        return self.test.price * self.quantity

