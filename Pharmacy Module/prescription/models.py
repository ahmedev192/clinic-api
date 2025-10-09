from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from medicine.models import Medicine


class Prescription(models.Model):
    """Prescription model for tracking prescriptions from consultation module"""
    
    PRESCRIPTION_STATUS = [
        ('pending', 'Pending'),
        ('dispensed', 'Dispensed'),
        ('partially_dispensed', 'Partially Dispensed'),
        ('cancelled', 'Cancelled'),
    ]

    # External reference to consultation (if integrated)
    consultation_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Consultation ID")
    prescription_number = models.CharField(max_length=50, unique=True, verbose_name="Prescription Number")
    
    # Patient information (basic fields, can be extended with patient model)
    patient_name = models.CharField(max_length=200, verbose_name="Patient Name")
    patient_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Patient ID")
    
    # Doctor information
    doctor_name = models.CharField(max_length=200, verbose_name="Doctor Name")
    doctor_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Doctor ID")
    
    # Prescription details
    prescription_date = models.DateField(default=timezone.now, verbose_name="Prescription Date")
    status = models.CharField(max_length=20, choices=PRESCRIPTION_STATUS, default='pending', verbose_name="Status")
    
    # Notes
    notes_en = models.TextField(blank=True, null=True, verbose_name="Notes (English)")
    notes_ar = models.TextField(blank=True, null=True, verbose_name="Notes (Arabic)")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_prescriptions')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_prescriptions')

    class Meta:
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prescription_number']),
            models.Index(fields=['patient_id']),
            models.Index(fields=['doctor_id']),
            models.Index(fields=['status']),
            models.Index(fields=['prescription_date']),
        ]

    def __str__(self):
        return f"Prescription {self.prescription_number} - {self.patient_name}"

    def get_total_items(self):
        """Get total number of items in the prescription"""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    def get_dispensed_items(self):
        """Get total number of dispensed items"""
        return self.items.aggregate(total=models.Sum('dispensed_quantity'))['total'] or 0

    def is_fully_dispensed(self):
        """Check if all items have been dispensed"""
        return all(item.quantity == item.dispensed_quantity for item in self.items.all())

    def update_status(self):
        """Update prescription status based on dispensed quantities"""
        if self.is_fully_dispensed():
            self.status = 'dispensed'
        elif any(item.dispensed_quantity > 0 for item in self.items.all()):
            self.status = 'partially_dispensed'
        else:
            self.status = 'pending'
        self.save()


class PrescriptionItem(models.Model):
    """Individual items in a prescription"""
    
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, verbose_name="Medicine")
    quantity = models.PositiveIntegerField(verbose_name="Quantity Prescribed")
    dispensed_quantity = models.PositiveIntegerField(default=0, verbose_name="Quantity Dispensed")
    
    # Dosage instructions
    dosage_instructions_en = models.TextField(blank=True, null=True, verbose_name="Dosage Instructions (English)")
    dosage_instructions_ar = models.TextField(blank=True, null=True, verbose_name="Dosage Instructions (Arabic)")
    
    # Notes
    notes_en = models.TextField(blank=True, null=True, verbose_name="Notes (English)")
    notes_ar = models.TextField(blank=True, null=True, verbose_name="Notes (Arabic)")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_prescription_items')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_prescription_items')

    class Meta:
        verbose_name = "Prescription Item"
        verbose_name_plural = "Prescription Items"
        ordering = ['medicine__name_en']
        unique_together = ['prescription', 'medicine']

    def __str__(self):
        return f"{self.medicine.name_en} - {self.quantity} units"

    def is_fully_dispensed(self):
        """Check if item is fully dispensed"""
        return self.dispensed_quantity >= self.quantity

    def get_remaining_quantity(self):
        """Get remaining quantity to be dispensed"""
        return max(0, self.quantity - self.dispensed_quantity)


class DispensingRecord(models.Model):
    """Record of dispensing operations"""
    
    prescription_item = models.ForeignKey(PrescriptionItem, on_delete=models.CASCADE, related_name='dispensing_records')
    quantity_dispensed = models.PositiveIntegerField(verbose_name="Quantity Dispensed")
    dispensing_date = models.DateTimeField(default=timezone.now, verbose_name="Dispensing Date")
    pharmacist_name = models.CharField(max_length=200, verbose_name="Pharmacist Name")
    pharmacist_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Pharmacist ID")
    
    # Stock reference
    stock_record = models.ForeignKey('stock.Stock', on_delete=models.SET_NULL, null=True, blank=True, related_name='dispensing_records')
    batch_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Batch Number")
    
    # Notes
    notes_en = models.TextField(blank=True, null=True, verbose_name="Notes (English)")
    notes_ar = models.TextField(blank=True, null=True, verbose_name="Notes (Arabic)")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_dispensing_records')

    class Meta:
        verbose_name = "Dispensing Record"
        verbose_name_plural = "Dispensing Records"
        ordering = ['-dispensing_date']
        indexes = [
            models.Index(fields=['prescription_item']),
            models.Index(fields=['dispensing_date']),
            models.Index(fields=['pharmacist_id']),
        ]

    def __str__(self):
        return f"{self.prescription_item.medicine.name_en} - {self.quantity_dispensed} units dispensed"
