"""
Utility functions for Staff Management
"""

from django.utils import timezone
from datetime import datetime, date, time
from typing import List, Dict, Optional
from .models import Staff, Doctor, Schedule


def get_staff_availability(staff_id: int, check_date: date, check_time: time) -> bool:
    """
    Check if a staff member is available at a specific date and time
    
    Args:
        staff_id: ID of the staff member
        check_date: Date to check availability
        check_time: Time to check availability
    
    Returns:
        bool: True if available, False otherwise
    """
    try:
        staff = Staff.objects.get(id=staff_id)
        day_of_week = check_date.weekday()
        
        # Check if staff has an active schedule for this day and time
        is_available = Schedule.objects.filter(
            staff=staff,
            day_of_week=day_of_week,
            start_time__lte=check_time,
            end_time__gte=check_time,
            is_active=True
        ).exists()
        
        # Additional checks for doctors
        if hasattr(staff, 'doctor_profile'):
            doctor = staff.doctor_profile
            is_available = is_available and doctor.is_available and doctor.is_accepting_new_patients
        
        return is_available
    except Staff.DoesNotExist:
        return False


def get_available_doctors_by_specialization(specialization_name: str) -> List[Doctor]:
    """
    Get all available doctors for a specific specialization
    
    Args:
        specialization_name: Name of the specialization
    
    Returns:
        List of available doctors
    """
    return Doctor.objects.filter(
        specializations__name_en__icontains=specialization_name,
        is_available=True,
        is_accepting_new_patients=True,
        staff__employment_status='active'
    ).select_related('staff').prefetch_related('specializations')


def get_weekly_schedule(staff_id: Optional[int] = None) -> Dict[int, List[Dict]]:
    """
    Get weekly schedule for all staff or specific staff member
    
    Args:
        staff_id: Optional staff ID to filter by
    
    Returns:
        Dictionary with day of week as key and list of schedules as value
    """
    queryset = Schedule.objects.filter(is_active=True)
    
    if staff_id:
        queryset = queryset.filter(staff_id=staff_id)
    
    weekly_schedule = {}
    
    for day in range(7):  # 0 = Monday, 6 = Sunday
        day_schedules = queryset.filter(day_of_week=day).select_related('staff')
        weekly_schedule[day] = [
            {
                'id': schedule.id,
                'staff_name': schedule.staff.full_name_en,
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'notes': schedule.notes
            }
            for schedule in day_schedules
        ]
    
    return weekly_schedule


def get_staff_statistics() -> Dict:
    """
    Get comprehensive staff statistics
    
    Returns:
        Dictionary with various staff statistics
    """
    from django.db.models import Count, Q
    
    # Basic counts
    total_staff = Staff.objects.filter(is_removed=False).count()
    active_staff = Staff.objects.filter(
        is_removed=False, 
        employment_status='active'
    ).count()
    
    # Count by role
    by_role = Staff.objects.filter(is_removed=False).values(
        'role__name_en'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Count by status
    by_status = Staff.objects.filter(is_removed=False).values(
        'employment_status'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Count by specialization
    by_specialization = Doctor.objects.filter(
        staff__is_removed=False,
        specializations__isnull=False
    ).values('specializations__name_en').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Specific role counts
    doctors = Staff.objects.filter(
        is_removed=False,
        role__code__in=['DOC', 'DOCTOR']
    ).count()
    
    nurses = Staff.objects.filter(
        is_removed=False,
        role__code='NURSE'
    ).count()
    
    receptionists = Staff.objects.filter(
        is_removed=False,
        role__code='RECEPTIONIST'
    ).count()
    
    return {
        'total_staff': total_staff,
        'active_staff': active_staff,
        'doctors': doctors,
        'nurses': nurses,
        'receptionists': receptionists,
        'by_role': {item['role__name_en']: item['count'] for item in by_role},
        'by_status': {item['employment_status']: item['count'] for item in by_status},
        'by_specialization': {item['specializations__name_en']: item['count'] for item in by_specialization}
    }


def format_staff_name(staff: Staff, language: str = 'en') -> str:
    """
    Format staff name based on language preference
    
    Args:
        staff: Staff instance
        language: 'en' for English, 'ar' for Arabic
    
    Returns:
        Formatted staff name
    """
    if language == 'ar':
        return f"{staff.first_name_ar} {staff.last_name_ar}"
    else:
        return f"{staff.first_name_en} {staff.last_name_en}"


def get_staff_by_role(role_code: str) -> List[Staff]:
    """
    Get all staff members by role code
    
    Args:
        role_code: Role code to filter by
    
    Returns:
        List of staff members
    """
    return Staff.objects.filter(
        role__code=role_code,
        is_removed=False,
        employment_status='active'
    ).select_related('role', 'user')


def is_doctor_available(doctor_id: int, check_date: date, check_time: time) -> bool:
    """
    Check if a doctor is available at a specific date and time
    
    Args:
        doctor_id: ID of the doctor
        check_date: Date to check availability
        check_time: Time to check availability
    
    Returns:
        bool: True if available, False otherwise
    """
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        
        # Check basic availability
        if not doctor.is_available or not doctor.is_accepting_new_patients:
            return False
        
        # Check schedule
        return get_staff_availability(doctor.staff.id, check_date, check_time)
    except Doctor.DoesNotExist:
        return False


def get_doctor_specializations(doctor_id: int) -> List[str]:
    """
    Get list of specializations for a doctor
    
    Args:
        doctor_id: ID of the doctor
    
    Returns:
        List of specialization names
    """
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        return [spec.name_en for spec in doctor.specializations.all()]
    except Doctor.DoesNotExist:
        return []


def validate_schedule_time(start_time: time, end_time: time) -> bool:
    """
    Validate that start time is before end time
    
    Args:
        start_time: Start time
        end_time: End time
    
    Returns:
        bool: True if valid, False otherwise
    """
    return start_time < end_time


def get_staff_working_hours(staff_id: int) -> Dict[int, List[Dict]]:
    """
    Get working hours for a specific staff member
    
    Args:
        staff_id: ID of the staff member
    
    Returns:
        Dictionary with day of week as key and working hours as value
    """
    try:
        staff = Staff.objects.get(id=staff_id)
        schedules = staff.schedules.filter(is_active=True)
        
        working_hours = {}
        for day in range(7):
            day_schedules = schedules.filter(day_of_week=day)
            working_hours[day] = [
                {
                    'start_time': schedule.start_time.strftime('%H:%M'),
                    'end_time': schedule.end_time.strftime('%H:%M'),
                    'notes': schedule.notes
                }
                for schedule in day_schedules
            ]
        
        return working_hours
    except Staff.DoesNotExist:
        return {}
