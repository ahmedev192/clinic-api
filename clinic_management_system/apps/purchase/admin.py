from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ['medicine', 'quantity', 'received_quantity', 'unit_cost', 'total_cost', 'batch_number', 'expiration_date']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact_person', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_person', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
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


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'order_date', 'expected_delivery_date', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'supplier', 'order_date', 'created_at']
    search_fields = ['order_number', 'supplier__name', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'subtotal', 'total_amount']
    inlines = [PurchaseOrderItemInline]
    list_per_page = 25
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'supplier', 'order_date', 'expected_delivery_date', 'actual_delivery_date', 'status')
        }),
        ('Financial Information', {
            'fields': ('subtotal', 'tax_amount', 'total_amount'),
            'classes': ('collapse',)
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


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'medicine', 'quantity', 'received_quantity', 'unit_cost', 'total_cost', 'is_fully_received']
    list_filter = ['purchase_order__status', 'created_at']
    search_fields = ['medicine__name_en', 'medicine__name_ar', 'purchase_order__order_number', 'batch_number']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'total_cost']
    list_per_page = 25
    
    fieldsets = (
        ('Item Information', {
            'fields': ('purchase_order', 'medicine', 'quantity', 'received_quantity')
        }),
        ('Pricing', {
            'fields': ('unit_cost', 'total_cost')
        }),
        ('Batch Information', {
            'fields': ('batch_number', 'expiration_date'),
            'classes': ('collapse',)
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
