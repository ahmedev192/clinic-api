"""
Custom validators for Staff Management
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validate_saudi_national_id(value):
    """
    Validate Saudi National ID format
    """
    if not value:
        return
    
    # Remove any non-digit characters
    clean_value = re.sub(r'\D', '', value)
    
    # Check if it's 10 digits
    if len(clean_value) != 10:
        raise ValidationError(_('Saudi National ID must be exactly 10 digits.'))
    
    # Check if it starts with 1 or 2
    if not clean_value.startswith(('1', '2')):
        raise ValidationError(_('Saudi National ID must start with 1 or 2.'))
    
    # Basic checksum validation (simplified)
    if not clean_value.isdigit():
        raise ValidationError(_('Saudi National ID must contain only digits.'))


def validate_phone_number(value):
    """
    Validate phone number format (Saudi format)
    """
    if not value:
        return
    
    # Remove any non-digit characters except +
    clean_value = re.sub(r'[^\d+]', '', value)
    
    # Check if it starts with +966 or 966
    if not (clean_value.startswith('+966') or clean_value.startswith('966')):
        raise ValidationError(_('Phone number must start with +966 or 966 for Saudi Arabia.'))
    
    # Check total length (should be 13 characters for +966XXXXXXXXX)
    if len(clean_value) != 13:
        raise ValidationError(_('Phone number must be in format +966XXXXXXXXX.'))


def validate_staff_id_format(value):
    """
    Validate staff ID format
    """
    if not value:
        return
    
    # Staff ID should be in format: ABC1234 (3 letters + 4 digits)
    pattern = r'^[A-Z]{3}\d{4}$'
    if not re.match(pattern, value):
        raise ValidationError(_('Staff ID must be in format ABC1234 (3 letters + 4 digits).'))


def validate_medical_license(value):
    """
    Validate medical license number format
    """
    if not value:
        return
    
    # Medical license should start with ML followed by digits
    pattern = r'^ML\d{6}$'
    if not re.match(pattern, value):
        raise ValidationError(_('Medical license must be in format ML123456.'))


def validate_consultation_fee(value):
    """
    Validate consultation fee
    """
    if value is None:
        return
    
    if value < 0:
        raise ValidationError(_('Consultation fee cannot be negative.'))
    
    if value > 10000:
        raise ValidationError(_('Consultation fee cannot exceed 10,000 SAR.'))


def validate_hourly_rate(value):
    """
    Validate hourly rate
    """
    if value is None:
        return
    
    if value < 0:
        raise ValidationError(_('Hourly rate cannot be negative.'))
    
    if value > 2000:
        raise ValidationError(_('Hourly rate cannot exceed 2,000 SAR per hour.'))


def validate_years_experience(value):
    """
    Validate years of experience
    """
    if value < 0:
        raise ValidationError(_('Years of experience cannot be negative.'))
    
    if value > 50:
        raise ValidationError(_('Years of experience cannot exceed 50 years.'))


def validate_salary_amount(value):
    """
    Validate salary amount
    """
    if value is None:
        return
    
    if value < 0:
        raise ValidationError(_('Salary cannot be negative.'))
    
    if value > 100000:
        raise ValidationError(_('Salary cannot exceed 100,000 SAR per month.'))


def validate_commission_percentage(value):
    """
    Validate commission percentage
    """
    if value is None:
        return
    
    if value < 0:
        raise ValidationError(_('Commission percentage cannot be negative.'))
    
    if value > 100:
        raise ValidationError(_('Commission percentage cannot exceed 100%.'))


def validate_bilingual_text(value_en, value_ar, field_name):
    """
    Validate that at least one language version is provided
    """
    if not value_en and not value_ar:
        raise ValidationError(_(f'{field_name} must be provided in at least one language (English or Arabic).'))


def validate_date_not_future(value):
    """
    Validate that date is not in the future
    """
    from django.utils import timezone
    
    if value and value > timezone.now().date():
        raise ValidationError(_('Date cannot be in the future.'))


def validate_joining_date_not_after_termination(joining_date, termination_date):
    """
    Validate that joining date is before termination date
    """
    if joining_date and termination_date and joining_date >= termination_date:
        raise ValidationError(_('Joining date must be before termination date.'))


def validate_schedule_time_conflict(staff, day_of_week, start_time, end_time, exclude_id=None):
    """
    Validate that schedule doesn't conflict with existing schedules
    """
    from .models import Schedule
    
    conflicting_schedules = Schedule.objects.filter(
        staff=staff,
        day_of_week=day_of_week,
        is_active=True
    ).exclude(id=exclude_id)
    
    for schedule in conflicting_schedules:
        # Check if times overlap
        if (start_time < schedule.end_time and end_time > schedule.start_time):
            raise ValidationError(
                _('Schedule conflicts with existing schedule: {} - {}').format(
                    schedule.start_time.strftime('%H:%M'),
                    schedule.end_time.strftime('%H:%M')
                )
            )
