"""
Appointments & Scheduling Models

This module contains all the models for the clinic appointments and scheduling system.
Supports bilingual data (Arabic and English) and provides comprehensive appointment management.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
import logging

logger = logging.getLogger(__name__)


class BilingualTextField(models.TextField):
    """
    Custom field to store bilingual text (Arabic and English).
    Stores data as JSON with 'en' and 'ar' keys.
    """
    
    def __init__(self, *args, **kwargs):
        kwargs['default'] = kwargs.get('default', dict)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        if isinstance(value, str):
            import json
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return {'en': value, 'ar': ''}
        return value
    
    def to_python(self, value):
        if isinstance(value, str):
            import json
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return {'en': value, 'ar': ''}
        return value
    
    def get_prep_value(self, value):
        if value is None:
            return value
        import json
        return json.dumps(value)


class TimeSlot(models.Model):
    """Represents a time slot for appointments."""
    
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(15), MaxValueValidator(480)]  # 15 min to 8 hours
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_time']
        unique_together = ['start_time', 'end_time']
    
    def __str__(self):
        return f"{self.start_time} - {self.end_time}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")


class Doctor(models.Model):
    """
    Doctor model - represents a doctor in the clinic.
    This is a simplified version that can be integrated with a full Doctors module later.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = BilingualTextField()
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def full_name_ar(self):
        # In a real implementation, this would come from a separate Arabic names field
        return self.user.get_full_name()


class Patient(models.Model):
    """
    Patient model - represents a patient in the clinic.
    This is a simplified version that can be integrated with a full Patients module later.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    patient_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.patient_id})"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class DoctorAvailability(models.Model):
    """Represents doctor's availability schedule."""
    
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    time_slot_duration = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(15), MaxValueValidator(120)]
    )
    is_recurring = models.BooleanField(default=True)
    specific_date = models.DateField(null=True, blank=True)  # For one-time availability
    is_active = models.BooleanField(default=True)
    notes = BilingualTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['doctor', 'day_of_week', 'start_time', 'end_time', 'specific_date']
    
    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK)[self.day_of_week]
        return f"{self.doctor} - {day_name} {self.start_time}-{self.end_time}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")
        if not self.is_recurring and not self.specific_date:
            raise ValidationError("Specific date is required for non-recurring availability.")


class AppointmentStatus(models.TextChoices):
    """Appointment status choices."""
    SCHEDULED = 'scheduled', 'Scheduled'
    CONFIRMED = 'confirmed', 'Confirmed'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    NO_SHOW = 'no_show', 'No Show'
    RESCHEDULED = 'rescheduled', 'Rescheduled'


class Appointment(models.Model):
    """Main appointment model."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_code = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=20, choices=AppointmentStatus.choices, default=AppointmentStatus.SCHEDULED)
    reason_for_visit = BilingualTextField()
    notes = BilingualTextField(blank=True, null=True)
    internal_notes = BilingualTextField(blank=True, null=True)  # For staff use only
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_appointments')
    cancellation_reason = BilingualTextField(blank=True, null=True)
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['appointment_date', 'appointment_time']),
            models.Index(fields=['status']),
            models.Index(fields=['patient']),
            models.Index(fields=['doctor']),
        ]
    
    def __str__(self):
        return f"{self.appointment_code} - {self.patient} with {self.doctor} on {self.appointment_date}"
    
    def save(self, *args, **kwargs):
        if not self.appointment_code:
            self.appointment_code = self.generate_appointment_code()
        super().save(*args, **kwargs)
    
    def generate_appointment_code(self):
        """Generate a unique appointment code."""
        import random
        import string
        while True:
            code = f"APT{''.join(random.choices(string.digits, k=6))}"
            if not Appointment.objects.filter(appointment_code=code).exists():
                return code
    
    @property
    def end_time(self):
        from datetime import timedelta
        from django.utils.dateparse import parse_time
        start_time = parse_time(str(self.appointment_time))
        end_time = (timezone.datetime.combine(self.appointment_date, start_time) + 
                   timedelta(minutes=self.duration_minutes)).time()
        return end_time
    
    def is_overlapping(self, other_appointment):
        """Check if this appointment overlaps with another."""
        if (self.doctor != other_appointment.doctor or 
            self.appointment_date != other_appointment.appointment_date):
            return False
        
        self_start = timezone.datetime.combine(self.appointment_date, self.appointment_time)
        self_end = self_start + timezone.timedelta(minutes=self.duration_minutes)
        other_start = timezone.datetime.combine(other_appointment.appointment_date, other_appointment.appointment_time)
        other_end = other_start + timezone.timedelta(minutes=other_appointment.duration_minutes)
        
        return not (self_end <= other_start or other_end <= self_start)


class WaitingList(models.Model):
    """Waiting list for appointments when slots are full."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='waiting_list_entries')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='waiting_list_entries')
    preferred_date = models.DateField()
    preferred_time_start = models.TimeField()
    preferred_time_end = models.TimeField()
    reason_for_visit = BilingualTextField()
    priority = models.IntegerField(default=0)  # Higher number = higher priority
    status = models.CharField(max_length=20, choices=[
        ('waiting', 'Waiting'),
        ('contacted', 'Contacted'),
        ('scheduled', 'Scheduled'),
        ('cancelled', 'Cancelled'),
    ], default='waiting')
    notes = BilingualTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    contacted_at = models.DateTimeField(null=True, blank=True)
    contacted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-priority', 'created_at']
        unique_together = ['patient', 'doctor', 'preferred_date']
    
    def __str__(self):
        return f"{self.patient} waiting for {self.doctor} on {self.preferred_date}"


class ReminderType(models.TextChoices):
    """Reminder type choices."""
    SMS = 'sms', 'SMS'
    EMAIL = 'email', 'Email'
    WHATSAPP = 'whatsapp', 'WhatsApp'
    PUSH = 'push', 'Push Notification'


class Reminder(models.Model):
    """Appointment reminders."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=ReminderType.choices)
    scheduled_time = models.DateTimeField()
    message_template = BilingualTextField()
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    delivery_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ], default='pending')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_time']
        indexes = [
            models.Index(fields=['scheduled_time', 'is_sent']),
            models.Index(fields=['appointment']),
        ]
    
    def __str__(self):
        return f"Reminder for {self.appointment.appointment_code} at {self.scheduled_time}"


class AppointmentAuditLog(models.Model):
    """Audit log for appointment changes."""
    
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
        ('reminder_sent', 'Reminder Sent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['appointment', 'timestamp']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.appointment.appointment_code} at {self.timestamp}"


class ClinicSettings(models.Model):
    """Clinic-wide settings for appointments."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic_name = BilingualTextField()
    default_appointment_duration = models.PositiveIntegerField(default=30)
    advance_booking_days = models.PositiveIntegerField(default=30)
    reminder_hours_before = models.JSONField(default=list)  # [24, 2] for 24h and 2h before
    working_hours_start = models.TimeField(default='08:00')
    working_hours_end = models.TimeField(default='17:00')
    timezone = models.CharField(max_length=50, default='UTC')
    allow_online_booking = models.BooleanField(default=True)
    require_confirmation = models.BooleanField(default=True)
    max_appointments_per_day = models.PositiveIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Clinic Settings'
        verbose_name_plural = 'Clinic Settings'
    
    def __str__(self):
        return f"Settings for {self.clinic_name.get('en', 'Clinic')}"
    
    @classmethod
    def get_settings(cls):
        """Get or create clinic settings."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
