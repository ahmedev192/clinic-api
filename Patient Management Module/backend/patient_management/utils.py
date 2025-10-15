"""
Patient Management Utilities

This module provides utility functions for patient management operations.
"""

import re
import uuid
from datetime import datetime, date
from django.utils import timezone
from django.core.exceptions import ValidationError
from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.validators import validate_international_phonenumber


def generate_patient_code():
    """
    Generate a unique patient code in format PAT-YYYY-XXXX
    """
    year = timezone.now().year
    from .models import Patient
    
    # Get the last patient code for this year
    last_patient = Patient.objects.filter(
        patient_code__startswith=f'PAT-{year}'
    ).order_by('-patient_code').first()
    
    if last_patient:
        # Extract the number part and increment
        try:
            last_number = int(last_patient.patient_code.split('-')[-1])
            new_number = last_number + 1
        except (ValueError, IndexError):
            new_number = 1
    else:
        new_number = 1
    
    return f'PAT-{year}-{new_number:04d}'


def validate_national_id(national_id):
    """
    Validate Saudi National ID format and checksum
    """
    if not national_id or not isinstance(national_id, str):
        raise ValidationError("National ID is required")
    
    # Remove any non-digit characters
    national_id = re.sub(r'\D', '', national_id)
    
    # Check length
    if len(national_id) != 10:
        raise ValidationError("National ID must be exactly 10 digits")
    
    # Check if all digits
    if not national_id.isdigit():
        raise ValidationError("National ID must contain only digits")
    
    # Basic checksum validation (simplified)
    # In a real implementation, you would implement the full Saudi ID checksum algorithm
    if national_id == '0000000000':
        raise ValidationError("Invalid National ID")
    
    return national_id


def validate_phone_number(phone_number):
    """
    Validate phone number format
    """
    if not phone_number:
        raise ValidationError("Phone number is required")
    
    try:
        validate_international_phonenumber(phone_number)
        return phone_number
    except ValidationError as e:
        raise ValidationError(f"Invalid phone number format: {e}")


def calculate_age(birth_date):
    """
    Calculate age from birth date
    """
    if not birth_date:
        return None
    
    today = timezone.now().date()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def format_patient_name(first_name_en, last_name_en, middle_name_en=None, 
                       first_name_ar=None, last_name_ar=None, middle_name_ar=None, 
                       language='en'):
    """
    Format patient name in specified language
    """
    if language == 'ar':
        name_parts = []
        if first_name_ar:
            name_parts.append(first_name_ar)
        if middle_name_ar:
            name_parts.append(middle_name_ar)
        if last_name_ar:
            name_parts.append(last_name_ar)
        return ' '.join(name_parts) if name_parts else None
    else:
        name_parts = [first_name_en]
        if middle_name_en:
            name_parts.append(middle_name_en)
        name_parts.append(last_name_en)
        return ' '.join(name_parts)


def generate_document_filename(patient_code, document_type, original_filename):
    """
    Generate a standardized filename for patient documents
    """
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    file_extension = original_filename.split('.')[-1] if '.' in original_filename else 'bin'
    return f"{patient_code}_{document_type}_{timestamp}.{file_extension}"


def validate_document_type(document_type):
    """
    Validate document type
    """
    valid_types = [
        'id_card', 'passport', 'insurance_card', 'lab_result', 'x_ray',
        'prescription', 'referral', 'medical_report', 'consent_form', 'other'
    ]
    
    if document_type not in valid_types:
        raise ValidationError(f"Invalid document type. Must be one of: {', '.join(valid_types)}")
    
    return document_type


def sanitize_filename(filename):
    """
    Sanitize filename for safe storage
    """
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores and dots
    filename = filename.strip('_.')
    # Ensure filename is not empty
    if not filename:
        filename = 'document'
    
    return filename


def get_patient_search_terms(query):
    """
    Extract search terms from query string for multilingual search
    """
    # Remove extra whitespace and split
    terms = re.sub(r'\s+', ' ', query.strip()).split()
    
    # Filter out very short terms (less than 2 characters)
    terms = [term for term in terms if len(term) >= 2]
    
    return terms


def is_arabic_text(text):
    """
    Check if text contains Arabic characters
    """
    if not text:
        return False
    
    # Arabic Unicode range: U+0600-U+06FF
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))


def is_english_text(text):
    """
    Check if text contains English characters
    """
    if not text:
        return False
    
    # English Unicode range: U+0020-U+007F
    english_pattern = re.compile(r'[a-zA-Z]')
    return bool(english_pattern.search(text))


def get_language_from_text(text):
    """
    Determine the primary language of text (Arabic or English)
    """
    if not text:
        return 'en'  # Default to English
    
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    if arabic_chars > english_chars:
        return 'ar'
    elif english_chars > 0:
        return 'en'
    else:
        return 'en'  # Default to English


def format_file_size(size_bytes):
    """
    Convert file size in bytes to human-readable format
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_blood_type(blood_type):
    """
    Validate blood type format
    """
    valid_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    
    if blood_type and blood_type not in valid_types:
        raise ValidationError(f"Invalid blood type. Must be one of: {', '.join(valid_types)}")
    
    return blood_type


def get_patient_statistics():
    """
    Get patient statistics for dashboard
    """
    from .models import Patient, MedicalHistory, Allergy, ChronicCondition
    
    stats = {
        'total_patients': Patient.objects.filter(is_deleted=False).count(),
        'active_patients': Patient.objects.filter(is_deleted=False, status='active').count(),
        'inactive_patients': Patient.objects.filter(is_deleted=False, status='inactive').count(),
        'archived_patients': Patient.objects.filter(is_deleted=False, status='archived').count(),
        'patients_this_month': Patient.objects.filter(
            is_deleted=False,
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).count(),
        'total_medical_records': MedicalHistory.objects.count(),
        'total_allergies': Allergy.objects.count(),
        'total_chronic_conditions': ChronicCondition.objects.count(),
    }
    
    return stats


def export_patients_to_csv(queryset, include_medical_data=False):
    """
    Export patients to CSV format
    """
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    headers = [
        'Patient Code', 'First Name (EN)', 'First Name (AR)', 'Last Name (EN)', 
        'Last Name (AR)', 'Gender', 'Date of Birth', 'Age', 'Phone Number', 
        'Email', 'National ID', 'Status', 'Created Date'
    ]
    
    if include_medical_data:
        headers.extend(['Blood Type', 'Allergies', 'Chronic Conditions'])
    
    writer.writerow(headers)
    
    # Data rows
    for patient in queryset:
        row = [
            patient.patient_code,
            patient.first_name_en,
            patient.first_name_ar,
            patient.last_name_en,
            patient.last_name_ar,
            patient.get_gender_display(),
            patient.date_of_birth,
            patient.get_age(),
            str(patient.phone_number),
            patient.email or '',
            patient.national_id,
            patient.get_status_display(),
            patient.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ]
        
        if include_medical_data:
            allergies = ', '.join([allergy.allergen_en for allergy in patient.allergies.all()])
            conditions = ', '.join([condition.condition_name_en for condition in patient.chronic_conditions.all()])
            row.extend([
                patient.blood_type or '',
                allergies,
                conditions
            ])
        
        writer.writerow(row)
    
    return output.getvalue()
