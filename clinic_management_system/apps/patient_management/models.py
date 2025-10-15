"""
Patient Management Models

This module contains all models for the patient management system,
including patient profiles, medical history, allergies, and document management.
"""

from django.db import models
from apps.accounts.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
import uuid
import os


class MultilingualTextField(models.TextField):
    """
    Custom field to handle multilingual text content.
    Stores both Arabic and English text in a single field.
    """
    def __init__(self, *args, **kwargs):
        kwargs['help_text'] = 'Enter text in both Arabic and English if needed'
        super().__init__(*args, **kwargs)


class MultilingualCharField(models.CharField):
    """
    Custom field to handle multilingual character content.
    Stores both Arabic and English text in a single field.
    """
    def __init__(self, *args, **kwargs):
        kwargs['help_text'] = 'Enter text in both Arabic and English if needed'
        super().__init__(*args, **kwargs)


def generate_patient_code():
    """Generate a unique patient code in format PAT-YYYY-XXXX"""
    year = timezone.now().year
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


def patient_document_upload_path(instance, filename):
    """Generate upload path for patient documents"""
    return f'patient_documents/{instance.patient.patient_code}/{filename}'


class Patient(models.Model):
    """
    Main Patient model containing all patient information.
    Supports multilingual content for names and notes.
    """
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    
    # Primary fields
    patient_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_patient_code,
        help_text='Unique patient identifier'
    )
    
    # Personal Information (Multilingual)
    first_name_en = models.CharField(max_length=100, help_text='First name in English')
    first_name_ar = models.CharField(max_length=100, blank=True, help_text='First name in Arabic')
    last_name_en = models.CharField(max_length=100, help_text='Last name in English')
    last_name_ar = models.CharField(max_length=100, blank=True, help_text='Last name in Arabic')
    middle_name_en = models.CharField(max_length=100, blank=True, help_text='Middle name in English')
    middle_name_ar = models.CharField(max_length=100, blank=True, help_text='Middle name in Arabic')
    
    # Demographics
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    
    # Contact Information
    phone_number = PhoneNumberField(unique=True, help_text='Primary phone number')
    secondary_phone = PhoneNumberField(blank=True, null=True, help_text='Secondary phone number')
    email = models.EmailField(blank=True, null=True)
    
    # Address (Multilingual)
    address_en = MultilingualTextField(help_text='Address in English')
    address_ar = models.TextField(blank=True, help_text='Address in Arabic')
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Saudi Arabia')
    
    # Identification
    national_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{10}$',
            message='National ID must be exactly 10 digits'
        )],
        help_text='National ID (10 digits)'
    )
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Medical Information
    blood_type = models.CharField(
        max_length=5,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        blank=True,
        null=True
    )
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = PhoneNumberField()
    emergency_contact_relationship = models.CharField(max_length=100)
    
    # Status and Metadata
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    notes = MultilingualTextField(blank=True, help_text='Additional notes about the patient')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='created_patients')
    updated_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='updated_patients')
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='deleted_patients',
        blank=True, 
        null=True
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_code']),
            models.Index(fields=['national_id']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.patient_code} - {self.get_full_name()}"
    
    def get_full_name(self):
        """Return full name in English"""
        name_parts = [self.first_name_en]
        if self.middle_name_en:
            name_parts.append(self.middle_name_en)
        name_parts.append(self.last_name_en)
        return ' '.join(name_parts)
    
    def get_full_name_ar(self):
        """Return full name in Arabic"""
        name_parts = [self.first_name_ar]
        if self.middle_name_ar:
            name_parts.append(self.middle_name_ar)
        name_parts.append(self.last_name_ar)
        return ' '.join(filter(None, name_parts))
    
    def get_age(self):
        """Calculate patient's age"""
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def soft_delete(self, user):
        """Soft delete the patient record"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.status = 'archived'
        self.save()


class MedicalHistory(models.Model):
    """
    Medical history entries for patients.
    Tracks diagnoses, treatments, and medical events.
    """
    
    CATEGORY_CHOICES = [
        ('diagnosis', 'Diagnosis'),
        ('surgery', 'Surgery'),
        ('treatment', 'Treatment'),
        ('hospitalization', 'Hospitalization'),
        ('vaccination', 'Vaccination'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_history')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Medical Information (Multilingual)
    title_en = models.CharField(max_length=200, help_text='Title in English')
    title_ar = models.CharField(max_length=200, blank=True, help_text='Title in Arabic')
    description_en = MultilingualTextField(help_text='Description in English')
    description_ar = models.TextField(blank=True, help_text='Description in Arabic')
    
    # Medical Details
    diagnosis_code = models.CharField(max_length=20, blank=True, help_text='ICD-10 code if applicable')
    treatment_notes = MultilingualTextField(blank=True, help_text='Treatment notes')
    
    # Dates
    event_date = models.DateField(help_text='Date when the medical event occurred')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    updated_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='updated_medical_history')
    
    class Meta:
        ordering = ['-event_date', '-created_at']
        verbose_name_plural = 'Medical Histories'
    
    def __str__(self):
        return f"{self.patient.patient_code} - {self.title_en} ({self.event_date})"


class Allergy(models.Model):
    """
    Patient allergy information.
    Tracks various types of allergies with severity levels.
    """
    
    ALLERGY_TYPE_CHOICES = [
        ('food', 'Food'),
        ('medication', 'Medication'),
        ('environmental', 'Environmental'),
        ('contact', 'Contact'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('life_threatening', 'Life Threatening'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    allergy_type = models.CharField(max_length=20, choices=ALLERGY_TYPE_CHOICES)
    
    # Allergy Information (Multilingual)
    allergen_en = models.CharField(max_length=200, help_text='Allergen name in English')
    allergen_ar = models.CharField(max_length=200, blank=True, help_text='Allergen name in Arabic')
    description_en = MultilingualTextField(help_text='Allergy description in English')
    description_ar = models.TextField(blank=True, help_text='Allergy description in Arabic')
    
    # Medical Details
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    symptoms = MultilingualTextField(help_text='Symptoms experienced')
    treatment_notes = MultilingualTextField(blank=True, help_text='Treatment for allergic reaction')
    
    # Dates
    first_occurrence = models.DateField(blank=True, null=True, help_text='Date of first occurrence')
    last_occurrence = models.DateField(blank=True, null=True, help_text='Date of last occurrence')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    updated_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='updated_allergies')
    
    class Meta:
        ordering = ['-severity', 'allergen_en']
        verbose_name_plural = 'Allergies'
    
    def __str__(self):
        return f"{self.patient.patient_code} - {self.allergen_en} ({self.severity})"


class ChronicCondition(models.Model):
    """
    Patient chronic conditions and diseases.
    Tracks ongoing medical conditions with management notes.
    """
    
    CONDITION_TYPE_CHOICES = [
        ('diabetes', 'Diabetes'),
        ('hypertension', 'Hypertension'),
        ('heart_disease', 'Heart Disease'),
        ('asthma', 'Asthma'),
        ('arthritis', 'Arthritis'),
        ('kidney_disease', 'Kidney Disease'),
        ('liver_disease', 'Liver Disease'),
        ('mental_health', 'Mental Health'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('critical', 'Critical'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='chronic_conditions')
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPE_CHOICES)
    
    # Condition Information (Multilingual)
    condition_name_en = models.CharField(max_length=200, help_text='Condition name in English')
    condition_name_ar = models.CharField(max_length=200, blank=True, help_text='Condition name in Arabic')
    description_en = MultilingualTextField(help_text='Condition description in English')
    description_ar = models.TextField(blank=True, help_text='Condition description in Arabic')
    
    # Medical Details
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    diagnosis_date = models.DateField(help_text='Date of diagnosis')
    icd_code = models.CharField(max_length=20, blank=True, help_text='ICD-10 code')
    
    # Management
    current_medications = MultilingualTextField(blank=True, help_text='Current medications for this condition')
    management_plan = MultilingualTextField(blank=True, help_text='Management plan and recommendations')
    notes = MultilingualTextField(blank=True, help_text='Additional notes')
    
    # Status
    is_active = models.BooleanField(default=True, help_text='Is this condition currently active?')
    last_review_date = models.DateField(blank=True, null=True, help_text='Date of last medical review')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    updated_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='updated_chronic_conditions')
    
    class Meta:
        ordering = ['-severity', 'condition_name_en']
        verbose_name_plural = 'Chronic Conditions'
    
    def __str__(self):
        return f"{self.patient.patient_code} - {self.condition_name_en} ({self.severity})"


class PatientDocument(models.Model):
    """
    Document management for patients.
    Stores various types of documents with metadata.
    """
    
    DOCUMENT_TYPE_CHOICES = [
        ('id_card', 'ID Card'),
        ('passport', 'Passport'),
        ('insurance_card', 'Insurance Card'),
        ('lab_result', 'Lab Result'),
        ('x_ray', 'X-Ray'),
        ('prescription', 'Prescription'),
        ('referral', 'Referral Letter'),
        ('medical_report', 'Medical Report'),
        ('consent_form', 'Consent Form'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    
    # Document Information (Multilingual)
    title_en = models.CharField(max_length=200, help_text='Document title in English')
    title_ar = models.CharField(max_length=200, blank=True, help_text='Document title in Arabic')
    description_en = MultilingualTextField(blank=True, help_text='Document description in English')
    description_ar = models.TextField(blank=True, help_text='Document description in Arabic')
    
    # File Information
    file = models.FileField(upload_to=patient_document_upload_path)
    file_size = models.PositiveIntegerField(help_text='File size in bytes')
    file_extension = models.CharField(max_length=10, help_text='File extension')
    
    # Metadata
    upload_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    
    # Document-specific fields
    document_date = models.DateField(blank=True, null=True, help_text='Date on the document')
    is_verified = models.BooleanField(default=False, help_text='Has this document been verified?')
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='verified_documents',
        blank=True, 
        null=True
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-upload_date']
        verbose_name_plural = 'Patient Documents'
    
    def __str__(self):
        return f"{self.patient.patient_code} - {self.title_en}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.file_extension = os.path.splitext(self.file.name)[1].lower()
        super().save(*args, **kwargs)
    
    def get_file_size_display(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class PatientSearchLog(models.Model):
    """
    Log patient searches for analytics and audit purposes.
    """
    searcher = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    search_query = models.CharField(max_length=200)
    search_filters = models.JSONField(default=dict)
    results_count = models.PositiveIntegerField()
    search_timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-search_timestamp']
    
    def __str__(self):
        return f"{self.searcher.username} - {self.search_query} ({self.results_count} results)"


