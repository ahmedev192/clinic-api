from django.db import models
from apps.accounts.models import User
from django.utils import timezone
from apps.medicine.models import Medicine


class Supplier(models.Model):
    """Supplier model for purchase orders"""
    
    name = models.CharField(max_length=200, verbose_name="Supplier Name")
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contact Person")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone")
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_suppliers')
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_suppliers')

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['name']

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    """Purchase order model for stock inflow"""
    
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
        ('partial', 'Partially Received'),
    ]

    order_number = models.CharField(max_length=50, unique=True, verbose_name="Order Number")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="Supplier")
    order_date = models.DateField(default=timezone.now, verbose_name="Order Date")
    expected_delivery_date = models.DateField(verbose_name="Expected Delivery Date")
    actual_delivery_date = models.DateField(null=True, blank=True, verbose_name="Actual Delivery Date")
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending', verbose_name="Status")
    
    # Financial information
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Subtotal")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Tax Amount")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Amount")
    
    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_purchase_orders')
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_purchase_orders')

    class Meta:
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['supplier', 'status']),
            models.Index(fields=['order_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"PO-{self.order_number} - {self.supplier.name}"

    def get_total_items(self):
        """Get total number of items in the order"""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    def get_received_items(self):
        """Get total number of received items"""
        return self.items.aggregate(total=models.Sum('received_quantity'))['total'] or 0

    def is_fully_received(self):
        """Check if all items have been received"""
        return all(item.quantity == item.received_quantity for item in self.items.all())

    def calculate_totals(self):
        """Calculate and update order totals"""
        items = self.items.all()
        self.subtotal = sum(item.quantity * item.unit_cost for item in items)
        self.total_amount = self.subtotal + self.tax_amount
        self.save()

    def mark_as_received(self):
        """Mark order as fully received"""
        if self.is_fully_received():
            self.status = 'received'
            self.actual_delivery_date = timezone.now().date()
            self.save()


class PurchaseOrderItem(models.Model):
    """Individual items in a purchase order"""
    
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, verbose_name="Medicine")
    quantity = models.PositiveIntegerField(verbose_name="Quantity Ordered")
    received_quantity = models.PositiveIntegerField(default=0, verbose_name="Quantity Received")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Unit Cost")
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total Cost")
    
    # Batch information (filled when received)
    batch_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Batch Number")
    expiration_date = models.DateField(null=True, blank=True, verbose_name="Expiration Date")
    
    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_purchase_items')
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_purchase_items')

    class Meta:
        verbose_name = "Purchase Order Item"
        verbose_name_plural = "Purchase Order Items"
        ordering = ['medicine__name_en']
        unique_together = ['purchase_order', 'medicine']

    def __str__(self):
        return f"{self.medicine.name_en} - {self.quantity} units"

    def save(self, *args, **kwargs):
        """Calculate total cost when saving"""
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def is_fully_received(self):
        """Check if item is fully received"""
        return self.received_quantity >= self.quantity

    def get_remaining_quantity(self):
        """Get remaining quantity to be received"""
        return max(0, self.quantity - self.received_quantity)


