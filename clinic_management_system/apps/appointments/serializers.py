"""
Serializers for the Appointments & Scheduling API.

Provides serialization for all models with proper validation and bilingual support.
"""

from rest_framework import serializers
from apps.accounts.models import User
from django.utils import timezone
from .models import (
    Doctor, Patient, DoctorAvailability, Appointment, WaitingList, 
    Reminder, AppointmentAuditLog, ClinicSettings, TimeSlot, AppointmentStatus
)


class BilingualField(serializers.Field):
    """Custom field for handling bilingual data."""
    
    def to_representation(self, value):
        if isinstance(value, dict):
            return value
        return {'en': str(value) if value else '', 'ar': ''}
    
    def to_internal_value(self, value):
        if isinstance(value, dict):
            return value
        return {'en': str(value) if value else '', 'ar': ''}


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = ['id', 'username']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for Doctor model."""
    
    user = UserSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    specialization = BilingualField()
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'user', 'employee_id', 'specialization', 'phone', 
            'is_active', 'full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model."""
    
    user = UserSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'patient_code', 'phone_number', 'date_of_birth', 
            'gender', 'status', 'full_name', 'age', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for TimeSlot model."""
    
    class Meta:
        model = TimeSlot
        fields = ['id', 'start_time', 'end_time', 'duration_minutes', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for DoctorAvailability model."""
    
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.UUIDField(write_only=True)
    notes = BilingualField()
    
    class Meta:
        model = DoctorAvailability
        fields = [
            'id', 'doctor', 'doctor_id', 'day_of_week', 'start_time', 'end_time',
            'time_slot_duration', 'is_recurring', 'specific_date', 'is_active',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Start time must be before end time.")
        
        if not data.get('is_recurring') and not data.get('specific_date'):
            raise serializers.ValidationError("Specific date is required for non-recurring availability.")
        
        return data


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model."""
    
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.UUIDField(write_only=True)
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.UUIDField(write_only=True)
    created_by = UserSerializer(read_only=True)
    cancelled_by = UserSerializer(read_only=True)
    reason_for_visit = BilingualField()
    notes = BilingualField()
    internal_notes = BilingualField()
    cancellation_reason = BilingualField()
    end_time = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'appointment_code', 'patient', 'patient_id', 'doctor', 'doctor_id',
            'appointment_date', 'appointment_time', 'duration_minutes', 'status',
            'reason_for_visit', 'notes', 'internal_notes', 'created_by',
            'created_at', 'updated_at', 'cancelled_at', 'cancelled_by',
            'cancellation_reason', 'end_time'
        ]
        read_only_fields = [
            'id', 'appointment_code', 'created_at', 'updated_at', 
            'cancelled_at', 'cancelled_by'
        ]
    
    def validate(self, data):
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        doctor_id = data.get('doctor_id')
        duration_minutes = data.get('duration_minutes', 30)
        
        if appointment_date and appointment_time and doctor_id:
            # Check if appointment is in the past
            appointment_datetime = timezone.datetime.combine(appointment_date, appointment_time)
            if appointment_datetime < timezone.now():
                raise serializers.ValidationError("Cannot schedule appointment in the past.")
            
            # Check for overlapping appointments
            if self.instance:
                # For updates, exclude current instance
                overlapping = Appointment.objects.filter(
                    doctor_id=doctor_id,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time
                ).exclude(id=self.instance.id)
            else:
                # For creation
                overlapping = Appointment.objects.filter(
                    doctor_id=doctor_id,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time
                )
            
            if overlapping.exists():
                raise serializers.ValidationError("Doctor already has an appointment at this time.")
        
        return data


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Specialized serializer for creating appointments."""
    
    patient_id = serializers.UUIDField()
    doctor_id = serializers.UUIDField()
    reason_for_visit = BilingualField()
    notes = BilingualField(required=False, allow_null=True)
    
    class Meta:
        model = Appointment
        fields = [
            'patient_id', 'doctor_id', 'appointment_date', 'appointment_time',
            'duration_minutes', 'reason_for_visit', 'notes'
        ]
    
    def validate(self, data):
        # Validate doctor availability
        doctor_id = data.get('doctor_id')
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        
        if doctor_id and appointment_date and appointment_time:
            # Check if doctor has availability on this day
            day_of_week = appointment_date.weekday()
            from django.db import models
            availability = DoctorAvailability.objects.filter(
                doctor_id=doctor_id,
                day_of_week=day_of_week,
                is_active=True
            ).filter(
                models.Q(is_recurring=True) | 
                models.Q(specific_date=appointment_date)
            )
            
            if not availability.exists():
                raise serializers.ValidationError("Doctor is not available on this date.")
            
            # Check if appointment time falls within available hours
            available_slots = []
            for avail in availability:
                if avail.start_time <= appointment_time < avail.end_time:
                    available_slots.append(avail)
            
            if not available_slots:
                raise serializers.ValidationError("Doctor is not available at this time.")
        
        return data
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class WaitingListSerializer(serializers.ModelSerializer):
    """Serializer for WaitingList model."""
    
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.UUIDField(write_only=True)
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.UUIDField(write_only=True)
    contacted_by = UserSerializer(read_only=True)
    reason_for_visit = BilingualField()
    notes = BilingualField()
    
    class Meta:
        model = WaitingList
        fields = [
            'id', 'patient', 'patient_id', 'doctor', 'doctor_id',
            'preferred_date', 'preferred_time_start', 'preferred_time_end',
            'reason_for_visit', 'priority', 'status', 'notes',
            'created_at', 'updated_at', 'contacted_at', 'contacted_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'contacted_at']


class ReminderSerializer(serializers.ModelSerializer):
    """Serializer for Reminder model."""
    
    appointment = AppointmentSerializer(read_only=True)
    appointment_id = serializers.UUIDField(write_only=True)
    message_template = BilingualField()
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'appointment', 'appointment_id', 'reminder_type',
            'scheduled_time', 'message_template', 'sent_at', 'is_sent',
            'delivery_status', 'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sent_at', 'is_sent', 'created_at', 'updated_at']


class AppointmentAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AppointmentAuditLog model."""
    
    performed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = AppointmentAuditLog
        fields = [
            'id', 'appointment', 'action', 'performed_by', 'old_values',
            'new_values', 'notes', 'timestamp', 'ip_address', 'user_agent'
        ]
        read_only_fields = ['id', 'timestamp']


class ClinicSettingsSerializer(serializers.ModelSerializer):
    """Serializer for ClinicSettings model."""
    
    clinic_name = BilingualField()
    
    class Meta:
        model = ClinicSettings
        fields = [
            'id', 'clinic_name', 'default_appointment_duration',
            'advance_booking_days', 'reminder_hours_before',
            'working_hours_start', 'working_hours_end', 'timezone',
            'allow_online_booking', 'require_confirmation',
            'max_appointments_per_day', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AppointmentSearchSerializer(serializers.Serializer):
    """Serializer for appointment search parameters."""
    
    patient_name = serializers.CharField(required=False)
    doctor_name = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=AppointmentStatus.choices, required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    doctor_id = serializers.UUIDField(required=False)
    patient_id = serializers.UUIDField(required=False)
    
    def validate(self, data):
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("date_from must be before date_to.")
        
        return data


class DoctorAvailabilitySearchSerializer(serializers.Serializer):
    """Serializer for doctor availability search."""
    
    doctor_id = serializers.UUIDField(required=False)
    date = serializers.DateField(required=False)
    day_of_week = serializers.IntegerField(min_value=0, max_value=6, required=False)
    is_recurring = serializers.BooleanField(required=False)


class AppointmentStatsSerializer(serializers.Serializer):
    """Serializer for appointment statistics."""
    
    total_appointments = serializers.IntegerField()
    scheduled_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    cancelled_appointments = serializers.IntegerField()
    no_show_appointments = serializers.IntegerField()
    today_appointments = serializers.IntegerField()
    upcoming_appointments = serializers.IntegerField()
    waiting_list_count = serializers.IntegerField()

