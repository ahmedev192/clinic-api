"""
Billing models for the Clinic Management System.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from model_utils import Choices
from model_utils.models import TimeStampedModel
import uuid


class MultilingualTextField(models.TextField):
    """Custom field for storing multilingual text data."""
    def __init__(self, *args, **kwargs):
        kwargs['help_text'] = 'Enter text in both English and Arabic (separated by " | ")'
        super().__init__(*args, **kwargs)


class MultilingualCharField(models.CharField):
    """Custom field for storing multilingual character data."""
    def __init__(self, *args, **kwargs):
        kwargs['help_text'] = 'Enter text in both English and Arabic (separated by " | ")'
        super().__init__(*args, **kwargs)


class Patient(models.Model):
    """Patient model for billing purposes."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.CharField(max_length=50, unique=True, help_text="External patient ID from main system")
    first_name_en = models.CharField(max_length=100)
    first_name_ar = models.CharField(max_length=100)
    last_name_en = models.CharField(max_length=100)
    last_name_ar = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name_en', 'first_name_en']

    def __str__(self):
        return f"{self.first_name_en} {self.last_name_en} ({self.patient_id})"

    @property
    def full_name_en(self):
        return f"{self.first_name_en} {self.last_name_en}"

    @property
    def full_name_ar(self):
        return f"{self.first_name_ar} {self.last_name_ar}"


class Doctor(models.Model):
    """Doctor model for billing purposes."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor_id = models.CharField(max_length=50, unique=True, help_text="External doctor ID from main system")
    first_name_en = models.CharField(max_length=100)
    first_name_ar = models.CharField(max_length=100)
    last_name_en = models.CharField(max_length=100)
    last_name_ar = models.CharField(max_length=100)
    specialization_en = models.CharField(max_length=200)
    specialization_ar = models.CharField(max_length=200)
    license_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name_en', 'first_name_en']

    def __str__(self):
        return f"Dr. {self.first_name_en} {self.last_name_en}"

    @property
    def full_name_en(self):
        return f"Dr. {self.first_name_en} {self.last_name_en}"

    @property
    def full_name_ar(self):
        return f"د. {self.first_name_ar} {self.last_name_ar}"


class ServiceCategory(models.Model):
    """Service category for organizing services."""
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['name_en']

    def __str__(self):
        return f"{self.name_en} | {self.name_ar}"


class Service(models.Model):
    """Service model for billable services."""
    SERVICE_TYPES = Choices(
        ('consultation', 'Consultation', 'Consultation'),
        ('lab_test', 'Lab Test', 'Lab Test'),
        ('pharmacy', 'Pharmacy', 'Pharmacy'),
        ('procedure', 'Procedure', 'Procedure'),
        ('other', 'Other', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_id = models.CharField(max_length=50, unique=True, help_text="External service ID from main system")
    name_en = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default=SERVICE_TYPES.consultation)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name_en']

    def __str__(self):
        return f"{self.name_en} | {self.name_ar}"


class Invoice(TimeStampedModel):
    """Invoice model for billing."""
    INVOICE_STATUS = Choices(
        ('draft', 'Draft', 'Draft'),
        ('pending', 'Pending Payment', 'Pending Payment'),
        ('paid', 'Paid', 'Paid'),
        ('cancelled', 'Cancelled', 'Cancelled'),
        ('refunded', 'Refunded', 'Refunded'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='invoices')
    visit_reference = models.CharField(max_length=100, blank=True, help_text="Reference to visit or appointment")
    service_reference = models.CharField(max_length=100, blank=True, help_text="Reference to specific service")
    
    # Financial fields
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default=INVOICE_STATUS.draft)
    notes_en = models.TextField(blank=True)
    notes_ar = models.TextField(blank=True)
    
    # Audit fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invoices')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_invoices')
    
    # Invoice dates
    invoice_date = models.DateTimeField()
    due_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created', '-invoice_date']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient.full_name_en}"

    def calculate_totals(self):
        """Calculate invoice totals including tax and discount."""
        # Calculate subtotal from items
        self.subtotal = sum(item.total_amount for item in self.items.all())
        
        # Calculate tax amount
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        
        # Calculate total amount
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        
        # Update outstanding amount
        self.outstanding_amount = self.total_amount - self.paid_amount

    def save(self, *args, **kwargs):
        # Calculate outstanding amount
        self.outstanding_amount = self.total_amount - self.paid_amount
        
        # Update status based on payment
        if self.paid_amount >= self.total_amount and self.total_amount > 0:
            self.status = self.INVOICE_STATUS.paid
        elif self.paid_amount > 0 and self.outstanding_amount > 0:
            self.status = self.INVOICE_STATUS.pending
        elif self.paid_amount == 0 and self.total_amount > 0:
            self.status = self.INVOICE_STATUS.pending
        
        super().save(*args, **kwargs)

    @property
    def is_fully_paid(self):
        return self.paid_amount >= self.total_amount

    @property
    def is_overdue(self):
        if not self.due_date:
            return False
        from django.utils import timezone
        return self.due_date < timezone.now() and not self.is_fully_paid


class InvoiceItem(models.Model):
    """Invoice item model for individual services/items."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='invoice_items')
    
    # Item details
    description_en = models.CharField(max_length=500)
    description_ar = models.CharField(max_length=500)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Reference fields
    service_reference = models.CharField(max_length=100, blank=True, help_text="Reference to specific service instance")
    notes_en = models.TextField(blank=True)
    notes_ar = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description_en}"

    def save(self, *args, **kwargs):
        # Calculate discount amount
        self.discount_amount = (self.unit_price * self.quantity * self.discount_percentage) / 100
        
        # Calculate total amount
        self.total_amount = (self.unit_price * self.quantity) - self.discount_amount
        
        super().save(*args, **kwargs)


class PaymentMethod(models.Model):
    """Payment method model."""
    PAYMENT_TYPES = Choices(
        ('cash', 'Cash', 'Cash'),
        ('card', 'Credit/Debit Card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer', 'Bank Transfer'),
        ('mobile_wallet', 'Mobile Wallet', 'Mobile Wallet'),
        ('insurance', 'Insurance', 'Insurance'),
        ('cheque', 'Cheque', 'Cheque'),
        ('other', 'Other', 'Other'),
    )

    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    is_active = models.BooleanField(default=True)
    requires_reference = models.BooleanField(default=False, help_text="Whether this payment method requires a reference number")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name_en']

    def __str__(self):
        return f"{self.name_en} | {self.name_ar}"


class Payment(TimeStampedModel):
    """Payment model for tracking payments."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    reference_number = models.CharField(max_length=100, blank=True, help_text="Transaction reference number")
    payment_date = models.DateTimeField()
    
    # Notes and metadata
    notes_en = models.TextField(blank=True)
    notes_ar = models.TextField(blank=True)
    
    # Audit fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payments')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_payments')
    
    # Status
    is_verified = models.BooleanField(default=False, help_text="Whether the payment has been verified")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verified_payments')
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-payment_date', '-created']

    def __str__(self):
        return f"Payment {self.amount} for Invoice {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice paid amount
        self.invoice.paid_amount = sum(payment.amount for payment in self.invoice.payments.filter(is_verified=True))
        self.invoice.save(update_fields=['paid_amount', 'outstanding_amount', 'status'])


class Refund(TimeStampedModel):
    """Refund model for tracking refunds."""
    REFUND_STATUS = Choices(
        ('pending', 'Pending', 'Pending'),
        ('approved', 'Approved', 'Approved'),
        ('processed', 'Processed', 'Processed'),
        ('cancelled', 'Cancelled', 'Cancelled'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='refunds')
    refund_number = models.CharField(max_length=50, unique=True)
    
    # Refund details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    reason_en = models.CharField(max_length=500)
    reason_ar = models.CharField(max_length=500)
    notes_en = models.TextField(blank=True)
    notes_ar = models.TextField(blank=True)
    
    # Status and processing
    status = models.CharField(max_length=20, choices=REFUND_STATUS, default=REFUND_STATUS.pending)
    processed_date = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_refunds')
    
    # Audit fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_refunds')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_refunds')

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Refund {self.refund_number} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.refund_number:
            self.refund_number = f"REF-{self.id.hex[:8].upper()}"
        super().save(*args, **kwargs)


class Discount(models.Model):
    """Discount model for promotions and manual discounts."""
    DISCOUNT_TYPES = Choices(
        ('percentage', 'Percentage', 'Percentage'),
        ('fixed', 'Fixed Amount', 'Fixed Amount'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_en = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    
    # Discount details
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    min_invoice_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of times this discount can be used")
    used_count = models.PositiveIntegerField(default=0)
    
    # Code for coupon-based discounts
    code = models.CharField(max_length=50, unique=True, blank=True, help_text="Coupon code for this discount")
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_discounts')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name_en} | {self.name_ar}"

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        return True

    def can_apply_to_invoice(self, invoice):
        """Check if this discount can be applied to the given invoice."""
        if not self.is_valid:
            return False
        if self.min_invoice_amount and invoice.subtotal < self.min_invoice_amount:
            return False
        return True

    def calculate_discount_amount(self, invoice_amount):
        """Calculate the discount amount for the given invoice amount."""
        if not self.can_apply_to_invoice_amount(invoice_amount):
            return 0
        
        if self.discount_type == self.DISCOUNT_TYPES.percentage:
            discount = (invoice_amount * self.value) / 100
        else:  # fixed
            discount = self.value
        
        if self.max_discount_amount:
            discount = min(discount, self.max_discount_amount)
        
        return min(discount, invoice_amount)

    def can_apply_to_invoice_amount(self, invoice_amount):
        """Check if this discount can be applied to the given invoice amount."""
        if not self.is_valid:
            return False
        if self.min_invoice_amount and invoice_amount < self.min_invoice_amount:
            return False
        return True


class AuditLog(models.Model):
    """Audit log for tracking all financial transactions."""
    ACTION_TYPES = Choices(
        ('invoice_created', 'Invoice Created', 'Invoice Created'),
        ('invoice_updated', 'Invoice Updated', 'Invoice Updated'),
        ('invoice_cancelled', 'Invoice Cancelled', 'Invoice Cancelled'),
        ('payment_created', 'Payment Created', 'Payment Created'),
        ('payment_verified', 'Payment Verified', 'Payment Verified'),
        ('refund_created', 'Refund Created', 'Refund Created'),
        ('refund_processed', 'Refund Processed', 'Refund Processed'),
        ('discount_applied', 'Discount Applied', 'Discount Applied'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Related objects
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, null=True, blank=True)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, null=True, blank=True)
    
    # Details
    description_en = models.TextField()
    description_ar = models.TextField()
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action_type} - {self.timestamp}"
