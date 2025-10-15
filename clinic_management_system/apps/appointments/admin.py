"""
Django admin configuration for the appointments app.

Provides comprehensive admin interface for managing appointments,
doctors, patients, and related data.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Appointment, DoctorAvailability, WaitingList, Reminder,
    AppointmentAuditLog, ClinicSettings, TimeSlot
)
from apps.staff_management.models import Doctor
from apps.patient_management.models import Patient


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    """Admin for TimeSlot model."""
    list_display = ['start_time', 'end_time', 'duration_minutes', 'is_active']
    list_filter = ['is_active']
    search_fields = ['start_time', 'end_time']
    ordering = ['start_time']


# Doctor and Patient admin registrations moved to their respective modules


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    """Admin for DoctorAvailability model."""
    list_display = ['doctor', 'day_of_week_display', 'start_time', 'end_time', 
                   'is_recurring', 'is_active', 'created_at']
    list_filter = ['day_of_week', 'is_recurring', 'is_active', 'created_at']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name']
    ordering = ['doctor', 'day_of_week', 'start_time']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def day_of_week_display(self, obj):
        """Display day of week as readable text."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[obj.day_of_week]
    day_of_week_display.short_description = 'Day of Week'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin for Appointment model."""
    list_display = ['appointment_code', 'patient', 'doctor', 'appointment_date', 
                   'appointment_time', 'status', 'created_at']
    list_filter = ['status', 'appointment_date', 'created_at', 'doctor']
    search_fields = ['appointment_code', 'patient__user__first_name', 
                    'patient__user__last_name', 'doctor__user__first_name', 
                    'doctor__user__last_name']
    ordering = ['-appointment_date', '-appointment_time']
    readonly_fields = ['id', 'appointment_code', 'created_at', 'updated_at', 
                      'cancelled_at', 'cancelled_by']
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('appointment_code', 'patient', 'doctor', 'appointment_date', 
                      'appointment_time', 'duration_minutes', 'status')
        }),
        ('Visit Details', {
            'fields': ('reason_for_visit', 'notes', 'internal_notes')
        }),
        ('Cancellation', {
            'fields': ('cancelled_at', 'cancelled_by', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'patient__user', 'doctor__user', 'created_by', 'cancelled_by'
        )


@admin.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):
    """Admin for WaitingList model."""
    list_display = ['patient', 'doctor', 'preferred_date', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority', 'preferred_date', 'created_at']
    search_fields = ['patient__user__first_name', 'patient__user__last_name',
                    'doctor__user__first_name', 'doctor__user__last_name']
    ordering = ['-priority', 'created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'contacted_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'patient__user', 'doctor__user', 'contacted_by'
        )


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    """Admin for Reminder model."""
    list_display = ['appointment', 'reminder_type', 'scheduled_time', 'is_sent', 
                   'delivery_status', 'created_at']
    list_filter = ['reminder_type', 'is_sent', 'delivery_status', 'created_at']
    search_fields = ['appointment__appointment_code']
    ordering = ['-scheduled_time']
    readonly_fields = ['id', 'sent_at', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'appointment__patient__user', 'appointment__doctor__user'
        )


@admin.register(AppointmentAuditLog)
class AppointmentAuditLogAdmin(admin.ModelAdmin):
    """Admin for AppointmentAuditLog model."""
    list_display = ['appointment', 'action', 'performed_by', 'timestamp']
    list_filter = ['action', 'timestamp', 'performed_by']
    search_fields = ['appointment__appointment_code', 'performed_by__username']
    ordering = ['-timestamp']
    readonly_fields = ['id', 'timestamp']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'appointment', 'performed_by'
        )


@admin.register(ClinicSettings)
class ClinicSettingsAdmin(admin.ModelAdmin):
    """Admin for ClinicSettings model."""
    list_display = ['clinic_name_display', 'default_appointment_duration', 
                   'advance_booking_days', 'allow_online_booking']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def clinic_name_display(self, obj):
        """Display clinic name in both languages."""
        name = obj.clinic_name
        if isinstance(name, dict):
            en = name.get('en', '')
            ar = name.get('ar', '')
            return f"{en} / {ar}" if ar else en
        return str(name)
    clinic_name_display.short_description = 'Clinic Name'
    
    def has_add_permission(self, request):
        """Only allow one settings instance."""
        return not ClinicSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of settings."""
        return False


# Customize admin site
admin.site.site_header = "Clinic Appointments & Scheduling Admin"
admin.site.site_title = "Appointments Admin"
admin.site.index_title = "Welcome to Appointments Administration"
