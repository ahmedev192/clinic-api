"""
Admin configuration for Staff Management
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Role, Specialization, Staff, Doctor, Schedule, 
    Compensation, StaffAuditLog
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_en', 'name_ar', 'is_active', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['code', 'name_en', 'name_ar']
    ordering = ['code']


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'is_active', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['name_en', 'name_ar']
    ordering = ['name_en']


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 0
    fields = ['day_of_week', 'start_time', 'end_time', 'is_active']


class CompensationInline(admin.TabularInline):
    model = Compensation
    extra = 0
    fields = ['compensation_type', 'base_salary', 'commission_percentage', 'effective_from']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = [
        'staff_id', 'full_name_en', 'role', 'employment_status', 
        'email', 'phone_primary', 'joining_date'
    ]
    list_filter = [
        'role', 'employment_status', 'gender', 'joining_date', 
        'created', 'is_removed'
    ]
    search_fields = [
        'staff_id', 'first_name_en', 'last_name_en', 'first_name_ar', 
        'last_name_ar', 'email', 'national_id'
    ]
    readonly_fields = ['staff_id', 'created', 'modified']
    inlines = [ScheduleInline, CompensationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'staff_id', 'user', 'role', 'employment_status',
                'joining_date', 'termination_date'
            )
        }),
        ('Personal Details (English)', {
            'fields': (
                'first_name_en', 'last_name_en', 'middle_name_en',
                'gender', 'date_of_birth'
            )
        }),
        ('Personal Details (Arabic)', {
            'fields': (
                'first_name_ar', 'last_name_ar', 'middle_name_ar'
            )
        }),
        ('Contact Information', {
            'fields': (
                'email', 'phone_primary', 'phone_secondary',
                'address_en', 'address_ar', 'city', 'country'
            )
        }),
        ('Identity', {
            'fields': ('national_id', 'passport_number')
        }),
        ('Profile', {
            'fields': ('profile_image',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created', 'modified'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('role', 'user')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = [
        'staff', 'medical_license_number', 'professional_title_en',
        'years_of_experience', 'is_available', 'is_accepting_new_patients'
    ]
    list_filter = [
        'is_available', 'is_accepting_new_patients', 'years_of_experience',
        'specializations', 'created'
    ]
    search_fields = [
        'staff__first_name_en', 'staff__last_name_en',
        'medical_license_number', 'professional_title_en'
    ]
    filter_horizontal = ['specializations']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('staff', 'medical_license_number')
        }),
        ('Professional Details (English)', {
            'fields': ('professional_title_en', 'biography_en')
        }),
        ('Professional Details (Arabic)', {
            'fields': ('professional_title_ar', 'biography_ar')
        }),
        ('Medical Information', {
            'fields': ('specializations', 'years_of_experience', 'languages')
        }),
        ('Financial Information', {
            'fields': ('consultation_fee', 'hourly_rate')
        }),
        ('Status', {
            'fields': ('is_available', 'is_accepting_new_patients')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('staff').prefetch_related('specializations')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'staff', 'day_of_week', 'start_time', 'end_time', 'is_active'
    ]
    list_filter = ['day_of_week', 'is_active', 'created']
    search_fields = ['staff__first_name_en', 'staff__last_name_en']
    ordering = ['staff', 'day_of_week', 'start_time']


@admin.register(Compensation)
class CompensationAdmin(admin.ModelAdmin):
    list_display = [
        'staff', 'compensation_type', 'base_salary', 
        'commission_percentage', 'effective_from'
    ]
    list_filter = ['compensation_type', 'effective_from', 'created']
    search_fields = ['staff__first_name_en', 'staff__last_name_en']
    ordering = ['staff', '-effective_from']


@admin.register(StaffAuditLog)
class StaffAuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'staff', 'action', 'field_name', 'changed_by', 'created'
    ]
    list_filter = ['action', 'created', 'changed_by']
    search_fields = ['staff__first_name_en', 'staff__last_name_en', 'field_name']
    readonly_fields = ['created']
    ordering = ['-created']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
