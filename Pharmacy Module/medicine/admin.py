from django.contrib import admin
from .models import Category, Medicine


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name_en', 'name_ar']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['internal_code', 'name_en', 'name_ar', 'category', 'dosage_form', 'strength', 'is_active', 'is_archived']
    list_filter = ['category', 'dosage_form', 'is_active', 'is_archived', 'created_at']
    search_fields = ['internal_code', 'name_en', 'name_ar', 'generic_name_en', 'generic_name_ar', 'brand_name_en', 'brand_name_ar']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('internal_code', 'name_en', 'name_ar', 'category')
        }),
        ('Names', {
            'fields': ('generic_name_en', 'generic_name_ar', 'brand_name_en', 'brand_name_ar')
        }),
        ('Specifications', {
            'fields': ('dosage_form', 'strength', 'unit')
        }),
        ('Inventory', {
            'fields': ('reorder_level', 'is_active', 'is_archived')
        }),
        ('Pricing', {
            'fields': ('base_cost', 'base_selling_price'),
            'classes': ('collapse',)
        }),
        ('Notes & Instructions', {
            'fields': ('notes_en', 'notes_ar', 'usage_instructions_en', 'usage_instructions_ar'),
            'classes': ('collapse',)
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
