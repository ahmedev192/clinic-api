from django.contrib import admin
from .models import Stock, StockAlert, StockTransaction


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'quantity', 'batch_number', 'expiration_date', 'is_active', 'stock_type', 'created_at']
    list_filter = ['is_active', 'stock_type', 'expiration_date', 'created_at']
    search_fields = ['medicine__name_en', 'medicine__name_ar', 'batch_number']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    list_per_page = 25
    
    fieldsets = (
        ('Medicine Information', {
            'fields': ('medicine', 'quantity', 'batch_number', 'expiration_date')
        }),
        ('Pricing', {
            'fields': ('purchase_cost', 'selling_price')
        }),
        ('Stock Management', {
            'fields': ('is_active', 'stock_type', 'purchase_order')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'alert_type', 'status', 'created_at', 'acknowledged_by']
    list_filter = ['alert_type', 'status', 'created_at']
    search_fields = ['medicine__name_en', 'medicine__name_ar', 'message']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'acknowledged_at']
    list_per_page = 25
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('medicine', 'stock_record', 'alert_type', 'status', 'message')
        }),
        ('Values', {
            'fields': ('threshold_value', 'actual_value')
        }),
        ('Acknowledgment', {
            'fields': ('acknowledged_by', 'acknowledged_at'),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'transaction_type', 'quantity_change', 'quantity_before', 'quantity_after', 'created_at', 'created_by']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['medicine__name_en', 'medicine__name_ar', 'reference_number', 'notes']
    readonly_fields = ['created_at', 'created_by']
    list_per_page = 25
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('medicine', 'stock_record', 'transaction_type', 'quantity_change', 'quantity_before', 'quantity_after')
        }),
        ('Reference', {
            'fields': ('reference_number', 'reference_type')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
