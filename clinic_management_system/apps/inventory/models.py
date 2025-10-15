"""
Inventory and Asset Management Models
"""
from django.db import models
from apps.accounts.models import User
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from django.core.validators import MinValueValidator
import uuid


class MultilingualTextField(models.TextField):
    """Custom field for storing multilingual text"""
    def __init__(self, *args, **kwargs):
        kwargs['help_text'] = 'Enter text in both Arabic and English separated by "|" (e.g., "English Text|النص العربي")'
        super().__init__(*args, **kwargs)


class Category(TimeStampedModel):
    """Item categories for better organization"""
    name_en = models.CharField(max_length=100, verbose_name=_('Name (English)'))
    name_ar = models.CharField(max_length=100, verbose_name=_('Name (Arabic)'))
    description_en = models.TextField(blank=True, verbose_name=_('Description (English)'))
    description_ar = models.TextField(blank=True, verbose_name=_('Description (Arabic)'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children', verbose_name=_('Parent Category'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name_en']
    
    def __str__(self):
        return f"{self.name_en} / {self.name_ar}"


class Supplier(TimeStampedModel):
    """Supplier information"""
    name_en = models.CharField(max_length=200, verbose_name=_('Name (English)'))
    name_ar = models.CharField(max_length=200, verbose_name=_('Name (Arabic)'))
    contact_person = models.CharField(max_length=100, verbose_name=_('Contact Person'))
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(max_length=20, verbose_name=_('Phone'))
    address_en = models.TextField(verbose_name=_('Address (English)'))
    address_ar = models.TextField(verbose_name=_('Address (Arabic)'))
    notes_en = models.TextField(blank=True, verbose_name=_('Notes (English)'))
    notes_ar = models.TextField(blank=True, verbose_name=_('Notes (Arabic)'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Supplier')
        verbose_name_plural = _('Suppliers')
        ordering = ['name_en']
    
    def __str__(self):
        return f"{self.name_en} / {self.name_ar}"


class Item(TimeStampedModel):
    """Inventory items and equipment"""
    ITEM_TYPES = [
        ('supply', _('Medical Supply')),
        ('equipment', _('Equipment')),
        ('tool', _('Tool')),
        ('consumable', _('Consumable')),
        ('furniture', _('Furniture')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('maintenance', _('Under Maintenance')),
        ('retired', _('Retired')),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', _('Excellent')),
        ('good', _('Good')),
        ('fair', _('Fair')),
        ('poor', _('Poor')),
        ('broken', _('Broken')),
    ]
    
    # Basic Information
    code = models.CharField(max_length=50, unique=True, verbose_name=_('Item Code'))
    name_en = models.CharField(max_length=200, verbose_name=_('Name (English)'))
    name_ar = models.CharField(max_length=200, verbose_name=_('Name (Arabic)'))
    description_en = models.TextField(blank=True, verbose_name=_('Description (English)'))
    description_ar = models.TextField(blank=True, verbose_name=_('Description (Arabic)'))
    
    # Classification
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, verbose_name=_('Item Type'))
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name=_('Category'))
    
    # Inventory Details
    current_quantity = models.PositiveIntegerField(default=0, verbose_name=_('Current Quantity'))
    unit = models.CharField(max_length=20, verbose_name=_('Unit'))
    reorder_level = models.PositiveIntegerField(default=0, verbose_name=_('Reorder Level'))
    location = models.CharField(max_length=100, verbose_name=_('Location'))
    
    # Status and Condition
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_('Status'))
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good', verbose_name=_('Condition'))
    
    # Supplier Information
    primary_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='primary_items', verbose_name=_('Primary Supplier'))
    suppliers = models.ManyToManyField(Supplier, blank=True, related_name='items', verbose_name=_('Suppliers'))
    
    # Financial Information
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                                   verbose_name=_('Unit Cost'))
    
    # Additional Fields
    barcode = models.CharField(max_length=100, blank=True, verbose_name=_('Barcode'))
    serial_number = models.CharField(max_length=100, blank=True, verbose_name=_('Serial Number'))
    expiry_date = models.DateField(null=True, blank=True, verbose_name=_('Expiry Date'))
    warranty_expiry = models.DateField(null=True, blank=True, verbose_name=_('Warranty Expiry'))
    
    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')
        ordering = ['name_en']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['item_type']),
            models.Index(fields=['status']),
            models.Index(fields=['current_quantity']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name_en} / {self.name_ar}"
    
    @property
    def is_low_stock(self):
        """Check if item is below reorder level"""
        return self.current_quantity <= self.reorder_level
    
    @property
    def is_expired(self):
        """Check if item has expired"""
        if self.expiry_date:
            from django.utils import timezone
            return self.expiry_date < timezone.now().date()
        return False


class StockMovement(TimeStampedModel):
    """Track all stock movements (in/out)"""
    MOVEMENT_TYPES = [
        ('in', _('Stock In')),
        ('out', _('Stock Out')),
        ('adjustment', _('Adjustment')),
        ('transfer', _('Transfer')),
        ('return', _('Return')),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='movements', verbose_name=_('Item'))
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES, verbose_name=_('Movement Type'))
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name=_('Quantity'))
    previous_quantity = models.PositiveIntegerField(verbose_name=_('Previous Quantity'))
    new_quantity = models.PositiveIntegerField(verbose_name=_('New Quantity'))
    
    # Transaction Details
    reference_number = models.CharField(max_length=100, blank=True, verbose_name=_('Reference Number'))
    notes_en = models.TextField(blank=True, verbose_name=_('Notes (English)'))
    notes_ar = models.TextField(blank=True, verbose_name=_('Notes (Arabic)'))
    
    # User and Department
    user = models.ForeignKey('accounts.User', on_delete=models.PROTECT, verbose_name=_('User'))
    department = models.CharField(max_length=100, blank=True, verbose_name=_('Department'))
    
    # Related Records
    purchase_order = models.ForeignKey('PurchaseOrder', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='movements', verbose_name=_('Purchase Order'))
    
    class Meta:
        verbose_name = _('Stock Movement')
        verbose_name_plural = _('Stock Movements')
        ordering = ['-created']
        indexes = [
            models.Index(fields=['item', 'created']),
            models.Index(fields=['movement_type']),
            models.Index(fields=['created']),
        ]
    
    def __str__(self):
        return f"{self.item.code} - {self.get_movement_type_display()} - {self.quantity}"


class PurchaseOrder(TimeStampedModel):
    """Purchase orders for stock replenishment"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('ordered', _('Ordered')),
        ('received', _('Received')),
        ('cancelled', _('Cancelled')),
        ('partial', _('Partially Received')),
    ]
    
    order_number = models.CharField(max_length=50, unique=True, verbose_name=_('Order Number'))
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name=_('Supplier'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('Status'))
    
    # Order Details
    order_date = models.DateTimeField(verbose_name=_('Order Date'))
    expected_delivery = models.DateField(verbose_name=_('Expected Delivery'))
    actual_delivery = models.DateField(null=True, blank=True, verbose_name=_('Actual Delivery'))
    
    # Financial Information
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('Subtotal'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('Tax Amount'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('Total Amount'))
    
    # Additional Information
    notes_en = models.TextField(blank=True, verbose_name=_('Notes (English)'))
    notes_ar = models.TextField(blank=True, verbose_name=_('Notes (Arabic)'))
    
    # User Information
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, verbose_name=_('Created By'))
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_orders', verbose_name=_('Approved By'))
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Approved At'))
    
    class Meta:
        verbose_name = _('Purchase Order')
        verbose_name_plural = _('Purchase Orders')
        ordering = ['-created']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['supplier']),
            models.Index(fields=['order_date']),
        ]
    
    def __str__(self):
        return f"PO-{self.order_number} - {self.supplier.name_en}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"PO-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class PurchaseOrderItem(TimeStampedModel):
    """Items in a purchase order"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, 
                                     related_name='items', verbose_name=_('Purchase Order'))
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name=_('Item'))
    quantity_ordered = models.PositiveIntegerField(verbose_name=_('Quantity Ordered'))
    quantity_received = models.PositiveIntegerField(default=0, verbose_name=_('Quantity Received'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Unit Price'))
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Total Price'))
    
    class Meta:
        verbose_name = _('Purchase Order Item')
        verbose_name_plural = _('Purchase Order Items')
        unique_together = ['purchase_order', 'item']
    
    def __str__(self):
        return f"{self.purchase_order.order_number} - {self.item.name_en}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity_ordered * self.unit_price
        super().save(*args, **kwargs)


class MaintenanceRecord(TimeStampedModel):
    """Equipment maintenance tracking"""
    MAINTENANCE_TYPES = [
        ('preventive', _('Preventive')),
        ('corrective', _('Corrective')),
        ('emergency', _('Emergency')),
        ('inspection', _('Inspection')),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='maintenance_records',
                           verbose_name=_('Item'))
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES, 
                                      verbose_name=_('Maintenance Type'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled',
                            verbose_name=_('Status'))
    
    # Maintenance Details
    scheduled_date = models.DateTimeField(verbose_name=_('Scheduled Date'))
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Completed Date'))
    next_maintenance_date = models.DateField(null=True, blank=True, verbose_name=_('Next Maintenance Date'))
    
    # Technician Information
    technician_name = models.CharField(max_length=100, verbose_name=_('Technician Name'))
    technician_contact = models.CharField(max_length=50, blank=True, verbose_name=_('Technician Contact'))
    
    # Description and Notes
    description_en = models.TextField(verbose_name=_('Description (English)'))
    description_ar = models.TextField(verbose_name=_('Description (Arabic)'))
    notes_en = models.TextField(blank=True, verbose_name=_('Notes (English)'))
    notes_ar = models.TextField(blank=True, verbose_name=_('Notes (Arabic)'))
    
    # Cost Information
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                              verbose_name=_('Maintenance Cost'))
    
    # User Information
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, verbose_name=_('Created By'))
    
    class Meta:
        verbose_name = _('Maintenance Record')
        verbose_name_plural = _('Maintenance Records')
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['item', 'scheduled_date']),
            models.Index(fields=['status']),
            models.Index(fields=['maintenance_type']),
        ]
    
    def __str__(self):
        return f"{self.item.name_en} - {self.get_maintenance_type_display()} - {self.scheduled_date.date()}"


class Alert(TimeStampedModel):
    """System alerts for low stock, expiry, etc."""
    ALERT_TYPES = [
        ('low_stock', _('Low Stock')),
        ('expired', _('Expired Item')),
        ('expiring_soon', _('Expiring Soon')),
        ('maintenance_due', _('Maintenance Due')),
        ('reorder', _('Reorder Required')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, verbose_name=_('Alert Type'))
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', 
                              verbose_name=_('Priority'))
    
    # Related Objects
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True, 
                           related_name='alerts', verbose_name=_('Item'))
    maintenance_record = models.ForeignKey(MaintenanceRecord, on_delete=models.CASCADE, 
                                        null=True, blank=True, related_name='alerts',
                                        verbose_name=_('Maintenance Record'))
    
    # Alert Details
    title_en = models.CharField(max_length=200, verbose_name=_('Title (English)'))
    title_ar = models.CharField(max_length=200, verbose_name=_('Title (Arabic)'))
    message_en = models.TextField(verbose_name=_('Message (English)'))
    message_ar = models.TextField(verbose_name=_('Message (Arabic)'))
    
    # Status
    is_read = models.BooleanField(default=False, verbose_name=_('Is Read'))
    is_resolved = models.BooleanField(default=False, verbose_name=_('Is Resolved'))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Resolved At'))
    resolved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='resolved_alerts', verbose_name=_('Resolved By'))
    
    class Meta:
        verbose_name = _('Alert')
        verbose_name_plural = _('Alerts')
        ordering = ['-created']
        indexes = [
            models.Index(fields=['alert_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_read', 'is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.title_en}"


