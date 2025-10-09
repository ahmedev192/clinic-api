from django.contrib import admin
from .models import Prescription, PrescriptionItem, DispensingRecord


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1
    fields = ['medicine', 'quantity', 'dispensed_quantity', 'dosage_instructions_en', 'dosage_instructions_ar']


class DispensingRecordInline(admin.TabularInline):
    model = DispensingRecord
    extra = 0
    fields = ['quantity_dispensed', 'dispensing_date', 'pharmacist_name', 'batch_number', 'notes_en', 'notes_ar']
    readonly_fields = ['created_at', 'created_by']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_number', 'patient_name', 'doctor_name', 'prescription_date', 'status', 'created_at']
    list_filter = ['status', 'prescription_date', 'created_at']
    search_fields = ['prescription_number', 'patient_name', 'doctor_name', 'patient_id', 'doctor_id']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    inlines = [PrescriptionItemInline]
    list_per_page = 25
    
    fieldsets = (
        ('Prescription Information', {
            'fields': ('prescription_number', 'consultation_id', 'prescription_date', 'status')
        }),
        ('Patient Information', {
            'fields': ('patient_name', 'patient_id')
        }),
        ('Doctor Information', {
            'fields': ('doctor_name', 'doctor_id')
        }),
        ('Notes', {
            'fields': ('notes_en', 'notes_ar'),
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


@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ['prescription', 'medicine', 'quantity', 'dispensed_quantity', 'is_fully_dispensed', 'created_at']
    list_filter = ['prescription__status', 'created_at']
    search_fields = ['medicine__name_en', 'medicine__name_ar', 'prescription__prescription_number']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    list_per_page = 25
    
    fieldsets = (
        ('Item Information', {
            'fields': ('prescription', 'medicine', 'quantity', 'dispensed_quantity')
        }),
        ('Dosage Instructions', {
            'fields': ('dosage_instructions_en', 'dosage_instructions_ar')
        }),
        ('Notes', {
            'fields': ('notes_en', 'notes_ar')
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


@admin.register(DispensingRecord)
class DispensingRecordAdmin(admin.ModelAdmin):
    list_display = ['prescription_item', 'quantity_dispensed', 'dispensing_date', 'pharmacist_name', 'batch_number']
    list_filter = ['dispensing_date', 'created_at']
    search_fields = ['prescription_item__medicine__name_en', 'prescription_item__medicine__name_ar', 'pharmacist_name', 'batch_number']
    readonly_fields = ['created_at', 'created_by']
    list_per_page = 25
    
    fieldsets = (
        ('Dispensing Information', {
            'fields': ('prescription_item', 'quantity_dispensed', 'dispensing_date', 'pharmacist_name', 'pharmacist_id')
        }),
        ('Stock Information', {
            'fields': ('stock_record', 'batch_number')
        }),
        ('Notes', {
            'fields': ('notes_en', 'notes_ar')
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
