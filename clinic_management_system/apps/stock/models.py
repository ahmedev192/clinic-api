from django.db import models
from apps.accounts.models import User
from django.utils import timezone
from apps.medicine.models import Medicine


class Stock(models.Model):
    """Stock model for tracking medicine inventory"""
    
    STOCK_TYPES = [
        ('purchase', 'Purchase'),
        ('adjustment', 'Manual Adjustment'),
        ('dispense', 'Dispensed'),
        ('return', 'Return'),
        ('transfer', 'Transfer'),
        ('expired', 'Expired'),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='stock_records')
    quantity = models.IntegerField(verbose_name="Quantity")
    batch_number = models.CharField(max_length=100, verbose_name="Batch/Lot Number")
    expiration_date = models.DateField(verbose_name="Expiration Date")
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Purchase Cost")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Selling Price")
    
    # Stock management
    is_active = models.BooleanField(default=True, verbose_name="Active")
    stock_type = models.CharField(max_length=20, choices=STOCK_TYPES, default='purchase', verbose_name="Stock Type")
    
    # Reference to purchase order (if applicable)
    purchase_order = models.ForeignKey('purchase.PurchaseOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_items')
    
    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_stock')
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_stock')

    class Meta:
        verbose_name = "Stock Record"
        verbose_name_plural = "Stock Records"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['medicine', 'is_active']),
            models.Index(fields=['expiration_date']),
            models.Index(fields=['batch_number']),
            models.Index(fields=['stock_type']),
        ]

    def __str__(self):
        return f"{self.medicine.name_en} - {self.quantity} units (Batch: {self.batch_number})"

    def is_expired(self):
        """Check if stock is expired"""
        return self.expiration_date < timezone.now().date()

    def is_expiring_soon(self, days=30):
        """Check if stock is expiring within specified days"""
        future_date = timezone.now().date() + timezone.timedelta(days=days)
        return self.expiration_date <= future_date and not self.is_expired()

    def get_days_until_expiry(self):
        """Get number of days until expiration"""
        if self.is_expired():
            return 0
        return (self.expiration_date - timezone.now().date()).days


class StockAlert(models.Model):
    """Model for tracking stock alerts and notifications"""
    
    ALERT_TYPES = [
        ('low_stock', 'Low Stock'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('reorder', 'Reorder Required'),
    ]

    ALERT_STATUS = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='alerts')
    stock_record = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, verbose_name="Alert Type")
    status = models.CharField(max_length=20, choices=ALERT_STATUS, default='active', verbose_name="Status")
    message = models.TextField(verbose_name="Alert Message")
    threshold_value = models.IntegerField(null=True, blank=True, verbose_name="Threshold Value")
    actual_value = models.IntegerField(null=True, blank=True, verbose_name="Actual Value")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_alerts')
    acknowledged_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Stock Alert"
        verbose_name_plural = "Stock Alerts"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['medicine', 'alert_type', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.medicine.name_en} - {self.get_alert_type_display()}"

    def acknowledge(self, user):
        """Acknowledge the alert"""
        self.status = 'acknowledged'
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save()

    def resolve(self):
        """Mark alert as resolved"""
        self.status = 'resolved'
        self.save()


class StockTransaction(models.Model):
    """Model for tracking all stock movements and changes"""
    
    TRANSACTION_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('return', 'Return'),
        ('expired', 'Expired'),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='transactions')
    stock_record = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="Transaction Type")
    quantity_change = models.IntegerField(verbose_name="Quantity Change")  # Positive for in, negative for out
    quantity_before = models.IntegerField(verbose_name="Quantity Before")
    quantity_after = models.IntegerField(verbose_name="Quantity After")
    
    # Reference information
    reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Reference Number")
    reference_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Reference Type")  # e.g., 'purchase_order', 'prescription'
    
    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_transactions')

    class Meta:
        verbose_name = "Stock Transaction"
        verbose_name_plural = "Stock Transactions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['medicine', 'transaction_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['reference_number']),
        ]

    def __str__(self):
        return f"{self.medicine.name_en} - {self.get_transaction_type_display()} ({self.quantity_change:+d})"


