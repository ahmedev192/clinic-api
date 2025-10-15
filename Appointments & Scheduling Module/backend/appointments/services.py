"""
Business logic services for the Appointments & Scheduling module.

This module contains all the business logic for managing appointments, availability,
waiting lists, and reminders. It's designed to be modular and reusable.
"""

import logging
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, Count, Case, When, IntegerField
from .models import (
    Appointment, DoctorAvailability, WaitingList, Reminder, 
    AppointmentAuditLog, Doctor, Patient, ClinicSettings
)

logger = logging.getLogger(__name__)


class AppointmentService:
    """Service class for managing appointments."""
    
    @staticmethod
    def create_appointment(
        patient_id: str,
        doctor_id: str,
        appointment_date: datetime.date,
        appointment_time: datetime.time,
        reason_for_visit: Dict[str, str],
        duration_minutes: int = 30,
        notes: Optional[Dict[str, str]] = None,
        created_by=None
    ) -> Appointment:
        """Create a new appointment with validation."""
        
        try:
            with transaction.atomic():
                # Validate doctor availability
                if not AppointmentService.is_doctor_available(
                    doctor_id, appointment_date, appointment_time, duration_minutes
                ):
                    raise ValidationError("Doctor is not available at the requested time.")
                
                # Check for overlapping appointments
                if AppointmentService.has_overlapping_appointment(
                    doctor_id, appointment_date, appointment_time, duration_minutes
                ):
                    raise ValidationError("Doctor already has an appointment at this time.")
                
                # Create appointment
                appointment = Appointment.objects.create(
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    duration_minutes=duration_minutes,
                    reason_for_visit=reason_for_visit,
                    notes=notes or {},
                    created_by=created_by
                )
                
                # Log the creation
                AppointmentAuditLog.objects.create(
                    appointment=appointment,
                    action='created',
                    performed_by=created_by,
                    new_values={
                        'patient_id': str(patient_id),
                        'doctor_id': str(doctor_id),
                        'appointment_date': appointment_date.isoformat(),
                        'appointment_time': appointment_time.isoformat(),
                        'reason_for_visit': reason_for_visit
                    }
                )
                
                logger.info(f"Appointment {appointment.appointment_code} created successfully")
                return appointment
                
        except Exception as e:
            logger.error(f"Failed to create appointment: {str(e)}")
            raise
    
    @staticmethod
    def is_doctor_available(
        doctor_id: str,
        appointment_date: datetime.date,
        appointment_time: datetime.time,
        duration_minutes: int = 30
    ) -> bool:
        """Check if doctor is available at the specified time."""
        
        day_of_week = appointment_date.weekday()
        
        # Check recurring availability
        recurring_availability = DoctorAvailability.objects.filter(
            doctor_id=doctor_id,
            day_of_week=day_of_week,
            is_recurring=True,
            is_active=True
        )
        
        # Check specific date availability
        specific_availability = DoctorAvailability.objects.filter(
            doctor_id=doctor_id,
            specific_date=appointment_date,
            is_active=True
        )
        
        all_availability = recurring_availability.union(specific_availability)
        
        if not all_availability.exists():
            return False
        
        # Check if time falls within available hours
        for availability in all_availability:
            if availability.start_time <= appointment_time < availability.end_time:
                return True
        
        return False
    
    @staticmethod
    def has_overlapping_appointment(
        doctor_id: str,
        appointment_date: datetime.date,
        appointment_time: datetime.time,
        duration_minutes: int = 30,
        exclude_appointment_id: Optional[str] = None
    ) -> bool:
        """Check if there's an overlapping appointment."""
        
        appointment_datetime = timezone.datetime.combine(appointment_date, appointment_time)
        end_datetime = appointment_datetime + timedelta(minutes=duration_minutes)
        
        queryset = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=appointment_date
        ).exclude(
            status__in=['cancelled', 'no_show']
        )
        
        if exclude_appointment_id:
            queryset = queryset.exclude(id=exclude_appointment_id)
        
        for appointment in queryset:
            existing_start = timezone.datetime.combine(
                appointment.appointment_date, 
                appointment.appointment_time
            )
            existing_end = existing_start + timedelta(minutes=appointment.duration_minutes)
            
            # Check for overlap
            if not (end_datetime <= existing_start or appointment_datetime >= existing_end):
                return True
        
        return False
    
    @staticmethod
    def reschedule_appointment(
        appointment_id: str,
        new_date: datetime.date,
        new_time: datetime.time,
        rescheduled_by=None,
        reason: Optional[Dict[str, str]] = None
    ) -> Appointment:
        """Reschedule an existing appointment."""
        
        try:
            with transaction.atomic():
                appointment = Appointment.objects.get(id=appointment_id)
                
                # Store old values for audit
                old_values = {
                    'appointment_date': appointment.appointment_date.isoformat(),
                    'appointment_time': appointment.appointment_time.isoformat()
                }
                
                # Validate new time
                if not AppointmentService.is_doctor_available(
                    appointment.doctor_id, new_date, new_time, appointment.duration_minutes
                ):
                    raise ValidationError("Doctor is not available at the new time.")
                
                if AppointmentService.has_overlapping_appointment(
                    appointment.doctor_id, new_date, new_time, 
                    appointment.duration_minutes, appointment_id
                ):
                    raise ValidationError("Doctor already has an appointment at the new time.")
                
                # Update appointment
                appointment.appointment_date = new_date
                appointment.appointment_time = new_time
                appointment.status = 'rescheduled'
                appointment.save()
                
                # Log the reschedule
                AppointmentAuditLog.objects.create(
                    appointment=appointment,
                    action='rescheduled',
                    performed_by=rescheduled_by,
                    old_values=old_values,
                    new_values={
                        'appointment_date': new_date.isoformat(),
                        'appointment_time': new_time.isoformat()
                    },
                    notes=reason
                )
                
                logger.info(f"Appointment {appointment.appointment_code} rescheduled successfully")
                return appointment
                
        except Appointment.DoesNotExist:
            raise ValidationError("Appointment not found")
        except Exception as e:
            logger.error(f"Failed to reschedule appointment: {str(e)}")
            raise
    
    @staticmethod
    def cancel_appointment(
        appointment_id: str,
        cancelled_by=None,
        reason: Optional[Dict[str, str]] = None
    ) -> Appointment:
        """Cancel an appointment."""
        
        try:
            with transaction.atomic():
                appointment = Appointment.objects.get(id=appointment_id)
                
                # Update appointment
                appointment.status = 'cancelled'
                appointment.cancelled_at = timezone.now()
                appointment.cancelled_by = cancelled_by
                appointment.cancellation_reason = reason or {}
                appointment.save()
                
                # Log the cancellation
                AppointmentAuditLog.objects.create(
                    appointment=appointment,
                    action='cancelled',
                    performed_by=cancelled_by,
                    new_values={
                        'status': 'cancelled',
                        'cancelled_at': timezone.now().isoformat(),
                        'cancellation_reason': reason
                    }
                )
                
                logger.info(f"Appointment {appointment.appointment_code} cancelled successfully")
                return appointment
                
        except Appointment.DoesNotExist:
            raise ValidationError("Appointment not found")
        except Exception as e:
            logger.error(f"Failed to cancel appointment: {str(e)}")
            raise
    
    @staticmethod
    def mark_appointment_completed(
        appointment_id: str,
        completed_by=None,
        notes: Optional[Dict[str, str]] = None
    ) -> Appointment:
        """Mark an appointment as completed."""
        
        try:
            with transaction.atomic():
                appointment = Appointment.objects.get(id=appointment_id)
                
                # Update appointment
                appointment.status = 'completed'
                if notes:
                    appointment.internal_notes = notes
                appointment.save()
                
                # Log the completion
                AppointmentAuditLog.objects.create(
                    appointment=appointment,
                    action='completed',
                    performed_by=completed_by,
                    new_values={'status': 'completed'},
                    notes=notes
                )
                
                logger.info(f"Appointment {appointment.appointment_code} marked as completed")
                return appointment
                
        except Appointment.DoesNotExist:
            raise ValidationError("Appointment not found")
        except Exception as e:
            logger.error(f"Failed to mark appointment as completed: {str(e)}")
            raise
    
    @staticmethod
    def get_appointment_statistics() -> Dict:
        """Get appointment statistics."""
        
        today = timezone.now().date()
        
        stats = Appointment.objects.aggregate(
            total=Count('id'),
            scheduled=Count('id', filter=Q(status='scheduled')),
            confirmed=Count('id', filter=Q(status='confirmed')),
            completed=Count('id', filter=Q(status='completed')),
            cancelled=Count('id', filter=Q(status='cancelled')),
            no_show=Count('id', filter=Q(status='no_show')),
            today=Count('id', filter=Q(appointment_date=today)),
            upcoming=Count('id', filter=Q(appointment_date__gt=today, status__in=['scheduled', 'confirmed']))
        )
        
        stats['waiting_list'] = WaitingList.objects.filter(status='waiting').count()
        
        return stats


class DoctorAvailabilityService:
    """Service class for managing doctor availability."""
    
    @staticmethod
    def get_available_slots(
        doctor_id: str,
        date: datetime.date,
        duration_minutes: int = 30
    ) -> List[Dict]:
        """Get available time slots for a doctor on a specific date."""
        
        day_of_week = date.weekday()
        
        # Get availability for this day
        availability = DoctorAvailability.objects.filter(
            doctor_id=doctor_id,
            day_of_week=day_of_week,
            is_recurring=True,
            is_active=True
        ).union(
            DoctorAvailability.objects.filter(
                doctor_id=doctor_id,
                specific_date=date,
                is_active=True
            )
        )
        
        if not availability.exists():
            return []
        
        # Get existing appointments for this date
        existing_appointments = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=date
        ).exclude(
            status__in=['cancelled', 'no_show']
        )
        
        available_slots = []
        
        for avail in availability:
            current_time = avail.start_time
            end_time = avail.end_time
            
            while current_time < end_time:
                slot_end = (datetime.combine(date, current_time) + 
                           timedelta(minutes=duration_minutes)).time()
                
                if slot_end > end_time:
                    break
                
                # Check if this slot conflicts with existing appointments
                is_available = True
                for appointment in existing_appointments:
                    if AppointmentService.has_overlapping_appointment(
                        doctor_id, date, current_time, duration_minutes
                    ):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append({
                        'start_time': current_time,
                        'end_time': slot_end,
                        'duration_minutes': duration_minutes
                    })
                
                # Move to next slot
                current_time = (datetime.combine(date, current_time) + 
                              timedelta(minutes=avail.time_slot_duration)).time()
        
        return available_slots
    
    @staticmethod
    def block_time_slot(
        doctor_id: str,
        date: datetime.date,
        start_time: datetime.time,
        end_time: datetime.time,
        reason: Dict[str, str],
        blocked_by=None
    ) -> DoctorAvailability:
        """Block a specific time slot for a doctor."""
        
        return DoctorAvailability.objects.create(
            doctor_id=doctor_id,
            day_of_week=date.weekday(),
            start_time=start_time,
            end_time=end_time,
            is_recurring=False,
            specific_date=date,
            is_active=True,
            notes=reason,
            time_slot_duration=30
        )


class WaitingListService:
    """Service class for managing waiting lists."""
    
    @staticmethod
    def add_to_waiting_list(
        patient_id: str,
        doctor_id: str,
        preferred_date: datetime.date,
        preferred_time_start: datetime.time,
        preferred_time_end: datetime.time,
        reason_for_visit: Dict[str, str],
        priority: int = 0,
        notes: Optional[Dict[str, str]] = None
    ) -> WaitingList:
        """Add a patient to the waiting list."""
        
        # Check if patient is already on waiting list for this doctor and date
        existing = WaitingList.objects.filter(
            patient_id=patient_id,
            doctor_id=doctor_id,
            preferred_date=preferred_date,
            status='waiting'
        ).first()
        
        if existing:
            raise ValidationError("Patient is already on the waiting list for this doctor and date.")
        
        return WaitingList.objects.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            preferred_date=preferred_date,
            preferred_time_start=preferred_time_start,
            preferred_time_end=preferred_time_end,
            reason_for_visit=reason_for_visit,
            priority=priority,
            notes=notes or {}
        )
    
    @staticmethod
    def promote_from_waiting_list(
        waiting_list_id: str,
        appointment_date: datetime.date,
        appointment_time: datetime.time,
        promoted_by=None
    ) -> Appointment:
        """Promote a waiting list entry to a confirmed appointment."""
        
        try:
            with transaction.atomic():
                waiting_entry = WaitingList.objects.get(id=waiting_list_id)
                
                # Create appointment
                appointment = AppointmentService.create_appointment(
                    patient_id=waiting_entry.patient_id,
                    doctor_id=waiting_entry.doctor_id,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    reason_for_visit=waiting_entry.reason_for_visit,
                    notes=waiting_entry.notes,
                    created_by=promoted_by
                )
                
                # Update waiting list entry
                waiting_entry.status = 'scheduled'
                waiting_entry.contacted_at = timezone.now()
                waiting_entry.contacted_by = promoted_by
                waiting_entry.save()
                
                logger.info(f"Waiting list entry {waiting_list_id} promoted to appointment {appointment.appointment_code}")
                return appointment
                
        except WaitingList.DoesNotExist:
            raise ValidationError("Waiting list entry not found")
        except Exception as e:
            logger.error(f"Failed to promote waiting list entry: {str(e)}")
            raise


class ReminderService:
    """Service class for managing appointment reminders."""
    
    @staticmethod
    def schedule_reminder(
        appointment_id: str,
        reminder_type: str,
        hours_before: int,
        message_template: Dict[str, str]
    ) -> Reminder:
        """Schedule a reminder for an appointment."""
        
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Calculate reminder time
        appointment_datetime = timezone.datetime.combine(
            appointment.appointment_date, 
            appointment.appointment_time
        )
        reminder_time = appointment_datetime - timedelta(hours=hours_before)
        
        return Reminder.objects.create(
            appointment=appointment,
            reminder_type=reminder_type,
            scheduled_time=reminder_time,
            message_template=message_template
        )
    
    @staticmethod
    def get_pending_reminders() -> List[Reminder]:
        """Get all pending reminders that need to be sent."""
        
        now = timezone.now()
        return Reminder.objects.filter(
            scheduled_time__lte=now,
            is_sent=False
        ).order_by('scheduled_time')
    
    @staticmethod
    def mark_reminder_sent(reminder_id: str, delivery_status: str = 'sent') -> Reminder:
        """Mark a reminder as sent."""
        
        reminder = Reminder.objects.get(id=reminder_id)
        reminder.is_sent = True
        reminder.sent_at = timezone.now()
        reminder.delivery_status = delivery_status
        reminder.save()
        
        # Log the reminder
        AppointmentAuditLog.objects.create(
            appointment=reminder.appointment,
            action='reminder_sent',
            performed_by=None,
            new_values={
                'reminder_type': reminder.reminder_type,
                'sent_at': reminder.sent_at.isoformat()
            }
        )
        
        return reminder


class SearchService:
    """Service class for searching appointments and related data."""
    
    @staticmethod
    def search_appointments(
        patient_name: Optional[str] = None,
        doctor_name: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime.date] = None,
        date_to: Optional[datetime.date] = None,
        doctor_id: Optional[str] = None,
        patient_id: Optional[str] = None
    ) -> List[Appointment]:
        """Search appointments with various filters."""
        
        queryset = Appointment.objects.select_related('patient__user', 'doctor__user')
        
        if patient_name:
            queryset = queryset.filter(
                Q(patient__user__first_name__icontains=patient_name) |
                Q(patient__user__last_name__icontains=patient_name)
            )
        
        if doctor_name:
            queryset = queryset.filter(
                Q(doctor__user__first_name__icontains=doctor_name) |
                Q(doctor__user__last_name__icontains=doctor_name)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        
        if date_from:
            queryset = queryset.filter(appointment_date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(appointment_date__lte=date_to)
        
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        return queryset.order_by('appointment_date', 'appointment_time')
