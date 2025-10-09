"""
Inventory admin configuration
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, Supplier, Item, StockMovement, PurchaseOrder,
    PurchaseOrderItem, MaintenanceRecord, Alert
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'parent', 'is_active', 'created']
    list_filter = ['is_active', 'parent', 'created']
    search_fields = ['name_en', 'name_ar', 'description_en', 'description_ar']
    ordering = ['name_en']
    list_editable = ['is_active']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'contact_person', 'email', 'phone', 'is_active', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['name_en', 'name_ar', 'contact_person', 'email', 'phone']
    ordering = ['name_en']
    list_editable = ['is_active']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name_en', 'name_ar', 'item_type', 'category', 'current_quantity',
        'unit', 'status', 'condition', 'location', 'is_low_stock_display', 'is_expired_display'
    ]
    list_filter = ['item_type', 'status', 'condition', 'category', 'suppliers', 'created']
    search_fields = ['code', 'name_en', 'name_ar', 'description_en', 'description_ar', 'barcode', 'serial_number']
    ordering = ['name_en']
    list_editable = ['status', 'condition']
    filter_horizontal = ['suppliers']
    readonly_fields = ['created', 'modified', 'is_low_stock', 'is_expired']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name_en', 'name_ar', 'description_en', 'description_ar')
        }),
        ('Classification', {
            'fields': ('item_type', 'category')
        }),
        ('Inventory Details', {
            'fields': ('current_quantity', 'unit', 'reorder_level', 'location')
        }),
        ('Status and Condition', {
            'fields': ('status', 'condition')
        }),
        ('Supplier Information', {
            'fields': ('primary_supplier', 'suppliers')
        }),
        ('Financial Information', {
            'fields': ('unit_cost',)
        }),
        ('Additional Information', {
            'fields': ('barcode', 'serial_number', 'expiry_date', 'warranty_expiry')
        }),
        ('System Information', {
            'fields': ('is_low_stock', 'is_expired', 'created', 'modified'),
            'classes': ('collapse',)
        }),
    )
    
    def is_low_stock_display(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: red;">⚠️ Low Stock</span>')
        return format_html('<span style="color: green;">✓ OK</span>')
    is_low_stock_display.short_description = 'Stock Status'
    
    def is_expired_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">⚠️ Expired</span>')
        return format_html('<span style="color: green;">✓ Valid</span>')
    is_expired_display.short_description = 'Expiry Status'


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    readonly_fields = ['total_price']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'supplier', 'status', 'order_date', 'expected_delivery',
        'total_amount', 'created_by', 'approved_by', 'created'
    ]
    list_filter = ['status', 'supplier', 'created_by', 'approved_by', 'order_date', 'created']
    search_fields = ['order_number', 'supplier__name_en', 'supplier__name_ar', 'notes_en', 'notes_ar']
    ordering = ['-created']
    inlines = [PurchaseOrderItemInline]
    readonly_fields = ['order_number', 'created', 'modified', 'approved_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'supplier', 'status')
        }),
        ('Dates', {
            'fields': ('order_date', 'expected_delivery', 'actual_delivery')
        }),
        ('Financial Information', {
            'fields': ('subtotal', 'tax_amount', 'total_amount')
        }),
        ('Notes', {
            'fields': ('notes_en', 'notes_ar')
        }),
        ('Approval Information', {
            'fields': ('created_by', 'approved_by', 'approved_at')
        }),
        ('System Information', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        'item', 'movement_type', 'quantity', 'previous_quantity', 'new_quantity',
        'user', 'department', 'created'
    ]
    list_filter = ['movement_type', 'user', 'department', 'created']
    search_fields = ['item__name_en', 'item__name_ar', 'reference_number', 'notes_en', 'notes_ar']
    ordering = ['-created']
    readonly_fields = ['created', 'modified']
    
    fieldsets = (
        ('Movement Information', {
            'fields': ('item', 'movement_type', 'quantity', 'previous_quantity', 'new_quantity')
        }),
        ('Reference Information', {
            'fields': ('reference_number', 'purchase_order')
        }),
        ('Notes', {
            'fields': ('notes_en', 'notes_ar')
        }),
        ('User Information', {
            'fields': ('user', 'department')
        }),
        ('System Information', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'item', 'maintenance_type', 'status', 'scheduled_date', 'completed_date',
        'technician_name', 'cost', 'created_by', 'created'
    ]
    list_filter = ['maintenance_type', 'status', 'created_by', 'scheduled_date', 'created']
    search_fields = ['item__name_en', 'item__name_ar', 'technician_name', 'description_en', 'description_ar']
    ordering = ['-scheduled_date']
    readonly_fields = ['created', 'modified']
    
    fieldsets = (
        ('Maintenance Information', {
            'fields': ('item', 'maintenance_type', 'status')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'completed_date', 'next_maintenance_date')
        }),
        ('Technician Information', {
            'fields': ('technician_name', 'technician_contact')
        }),
        ('Description and Notes', {
            'fields': ('description_en', 'description_ar', 'notes_en', 'notes_ar')
        }),
        ('Cost Information', {
            'fields': ('cost',)
        }),
        ('User Information', {
            'fields': ('created_by',)
        }),
        ('System Information', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = [
        'alert_type', 'priority', 'title_en', 'item', 'is_read', 'is_resolved',
        'created', 'resolved_by'
    ]
    list_filter = ['alert_type', 'priority', 'is_read', 'is_resolved', 'created']
    search_fields = ['title_en', 'title_ar', 'message_en', 'message_ar', 'item__name_en', 'item__name_ar']
    ordering = ['-created']
    readonly_fields = ['created', 'modified', 'resolved_at']
    list_editable = ['is_read', 'is_resolved']
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_type', 'priority', 'title_en', 'title_ar')
        }),
        ('Message', {
            'fields': ('message_en', 'message_ar')
        }),
        ('Related Objects', {
            'fields': ('item', 'maintenance_record')
        }),
        ('Status', {
            'fields': ('is_read', 'is_resolved', 'resolved_at', 'resolved_by')
        }),
        ('System Information', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )
