"""
Django models for the Consultation & Clinical Notes Module.
Supports multilingual data (Arabic + English) and integration with other modules.
"""

from django.db import models
from apps.accounts.models import User
from django.utils import timezone
from model_utils import Choices
from model_utils.models import TimeStampedModel, SoftDeletableModel
import uuid


class MultilingualTextField(models.TextField):
    """Custom field for storing multilingual text data."""
    pass


class MultilingualCharField(models.CharField):
    """Custom field for storing multilingual character data."""
    pass


class Consultation(TimeStampedModel, SoftDeletableModel):
    """
    Main consultation model linking patients, doctors, and appointments.
    Supports both draft and completed states.
    """
    
    CONSULTATION_TYPES = Choices(
        ('new', 'New Consultation'),
        ('follow_up', 'Follow-up'),
        ('emergency', 'Emergency'),
        ('routine', 'Routine Check-up'),
    )
    
    STATUS_CHOICES = Choices(
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation_code = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Unique consultation reference code"
    )
    
    # Core relationships (integration points)
    from apps.patient_management.models import Patient
    from apps.staff_management.models import Doctor
    from apps.appointments.models import Appointment
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='consultations',
        help_text="Reference to Patient from Patients Module",
        null=True,
        blank=True
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='consultations',
        help_text="Reference to Doctor from Doctors Module",
        null=True,
        blank=True
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultations',
        help_text="Reference to Appointment from Appointments Module"
    )
    
    # Consultation details
    consultation_type = models.CharField(
        max_length=20,
        choices=CONSULTATION_TYPES,
        default=CONSULTATION_TYPES.new
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CHOICES.draft
    )
    
    # Multilingual fields
    chief_complaint_en = models.TextField(
        blank=True,
        help_text="Primary complaint in English"
    )
    chief_complaint_ar = models.TextField(
        blank=True,
        help_text="Primary complaint in Arabic"
    )
    
    symptoms_en = models.TextField(
        blank=True,
        help_text="Symptoms description in English"
    )
    symptoms_ar = models.TextField(
        blank=True,
        help_text="Symptoms description in Arabic"
    )
    
    examination_findings_en = models.TextField(
        blank=True,
        help_text="Physical examination findings in English"
    )
    examination_findings_ar = models.TextField(
        blank=True,
        help_text="Physical examination findings in Arabic"
    )
    
    assessment_notes_en = models.TextField(
        blank=True,
        help_text="Clinical assessment in English"
    )
    assessment_notes_ar = models.TextField(
        blank=True,
        help_text="Clinical assessment in Arabic"
    )
    
    # Consultation metadata
    consultation_date = models.DateTimeField(default=timezone.now)
    duration_minutes = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Consultation duration in minutes"
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='consultations_created'
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='consultations_updated',
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-consultation_date']
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['doctor']),
            models.Index(fields=['consultation_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Consultation {self.consultation_code} - Patient {self.patient.id if self.patient else 'N/A'}"
    
    def get_chief_complaint(self, language='en'):
        """Get chief complaint in specified language."""
        return getattr(self, f'chief_complaint_{language}', '')
    
    def get_symptoms(self, language='en'):
        """Get symptoms in specified language."""
        return getattr(self, f'symptoms_{language}', '')
    
    def get_examination_findings(self, language='en'):
        """Get examination findings in specified language."""
        return getattr(self, f'examination_findings_{language}', '')


class Diagnosis(TimeStampedModel, SoftDeletableModel):
    """
    Reusable diagnosis entries with multilingual support.
    Links to consultations and maintains patient history.
    """
    
    SEVERITY_LEVELS = Choices(
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('critical', 'Critical'),
    )
    
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    diagnosis_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Standardized diagnosis code (e.g., ICD-10)"
    )
    
    # Multilingual diagnosis details
    name_en = models.CharField(
        max_length=200,
        help_text="Diagnosis name in English"
    )
    name_ar = models.CharField(
        max_length=200,
        help_text="Diagnosis name in Arabic"
    )
    
    description_en = models.TextField(
        blank=True,
        help_text="Detailed description in English"
    )
    description_ar = models.TextField(
        blank=True,
        help_text="Detailed description in Arabic"
    )
    
    category = models.CharField(
        max_length=100,
        help_text="Diagnosis category or specialty"
    )
    
    # Diagnosis metadata
    is_chronic = models.BooleanField(default=False)
    is_contagious = models.BooleanField(default=False)
    severity_level = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        default=SEVERITY_LEVELS.mild
    )
    
    class Meta:
        ordering = ['name_en']
        indexes = [
            models.Index(fields=['diagnosis_code']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name_en} ({self.diagnosis_code})"
    
    def get_name(self, language='en'):
        """Get diagnosis name in specified language."""
        return getattr(self, f'name_{language}', '')


class ConsultationDiagnosis(TimeStampedModel):
    """
    Junction model linking consultations with diagnoses.
    Tracks diagnosis-specific notes and status.
    """
    
    DIAGNOSIS_STATUS = Choices(
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('differential', 'Differential'),
        ('ruled_out', 'Ruled Out'),
    )
    
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='diagnoses'
    )
    diagnosis = models.ForeignKey(
        Diagnosis,
        on_delete=models.CASCADE,
        related_name='consultation_instances'
    )
    
    # Diagnosis-specific details
    status = models.CharField(
        max_length=20,
        choices=DIAGNOSIS_STATUS,
        default=DIAGNOSIS_STATUS.primary
    )
    
    notes_en = models.TextField(
        blank=True,
        help_text="Diagnosis-specific notes in English"
    )
    notes_ar = models.TextField(
        blank=True,
        help_text="Diagnosis-specific notes in Arabic"
    )
    
    # Clinical details
    onset_date = models.DateField(
        null=True,
        blank=True,
        help_text="When the condition started"
    )
    is_resolved = models.BooleanField(default=False)
    resolution_date = models.DateField(
        null=True,
        blank=True
    )
    
    class Meta:
        unique_together = ['consultation', 'diagnosis']
        ordering = ['status', 'diagnosis__name_en']
    
    def __str__(self):
        return f"{self.consultation.consultation_code} - {self.diagnosis.name_en}"


class Prescription(TimeStampedModel, SoftDeletableModel):
    """
    Prescription container linked to consultations.
    Contains multiple prescription items.
    """
    
    PRESCRIPTION_STATUS = Choices(
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique prescription reference code"
    )
    
    # Relationships
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    
    # Prescription details
    status = models.CharField(
        max_length=20,
        choices=PRESCRIPTION_STATUS,
        default=PRESCRIPTION_STATUS.draft
    )
    
    # Multilingual notes
    notes_en = models.TextField(
        blank=True,
        help_text="General prescription notes in English"
    )
    notes_ar = models.TextField(
        blank=True,
        help_text="General prescription notes in Arabic"
    )
    
    # Prescription metadata
    prescribed_date = models.DateTimeField(default=timezone.now)
    valid_until = models.DateField(
        null=True,
        blank=True,
        help_text="Prescription validity period"
    )
    
    # Integration with Pharmacy Module
    pharmacy_status = models.CharField(
        max_length=20,
        default='pending',
        help_text="Status from Pharmacy Module perspective"
    )
    pharmacy_notes = models.TextField(
        blank=True,
        help_text="Notes from pharmacy staff"
    )
    
    class Meta:
        ordering = ['-prescribed_date']
        indexes = [
            models.Index(fields=['consultation']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Prescription {self.prescription_code} - {self.consultation.consultation_code}"


class PrescriptionItem(TimeStampedModel):
    """
    Individual medication items within a prescription.
    Supports multilingual medication names and instructions.
    """
    
    FREQUENCY_CHOICES = Choices(
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('three_times_daily', 'Three Times Daily'),
        ('four_times_daily', 'Four Times Daily'),
        ('as_needed', 'As Needed'),
        ('custom', 'Custom'),
    )
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    # Medication details (multilingual)
    medication_name_en = models.CharField(
        max_length=200,
        help_text="Medication name in English"
    )
    medication_name_ar = models.CharField(
        max_length=200,
        help_text="Medication name in Arabic"
    )
    
    generic_name_en = models.CharField(
        max_length=200,
        blank=True,
        help_text="Generic name in English"
    )
    generic_name_ar = models.CharField(
        max_length=200,
        blank=True,
        help_text="Generic name in Arabic"
    )
    
    # Dosage information
    dosage = models.CharField(
        max_length=100,
        help_text="Dosage amount (e.g., 500mg, 1 tablet)"
    )
    frequency = models.CharField(
        max_length=30,
        choices=FREQUENCY_CHOICES,
        default=FREQUENCY_CHOICES.twice_daily
    )
    custom_frequency = models.CharField(
        max_length=100,
        blank=True,
        help_text="Custom frequency instructions"
    )
    
    # Duration and quantity
    duration_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Duration in days"
    )
    quantity = models.PositiveIntegerField(
        help_text="Total quantity prescribed"
    )
    
    # Instructions (multilingual)
    instructions_en = models.TextField(
        blank=True,
        help_text="Special instructions in English"
    )
    instructions_ar = models.TextField(
        blank=True,
        help_text="Special instructions in Arabic"
    )
    
    # Medication metadata
    is_controlled_substance = models.BooleanField(default=False)
    requires_refrigerator = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.medication_name_en} - {self.dosage}"
    
    def get_medication_name(self, language='en'):
        """Get medication name in specified language."""
        return getattr(self, f'medication_name_{language}', '')
    
    def get_instructions(self, language='en'):
        """Get instructions in specified language."""
        return getattr(self, f'instructions_{language}', '')


class LabOrder(TimeStampedModel, SoftDeletableModel):
    """
    Laboratory and imaging test orders from consultations.
    Integrates with Laboratory Module.
    """
    
    PRIORITY_LEVELS = Choices(
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('stat', 'STAT (Immediate)'),
    )
    
    ORDER_STATUS = Choices(
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique lab order reference code"
    )
    
    # Relationships
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='lab_orders'
    )
    
    # Test details (multilingual)
    test_name_en = models.CharField(
        max_length=200,
        help_text="Test name in English"
    )
    test_name_ar = models.CharField(
        max_length=200,
        help_text="Test name in Arabic"
    )
    
    test_category = models.CharField(
        max_length=100,
        help_text="Test category (e.g., Blood Test, X-Ray, MRI)"
    )
    
    # Order details
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_LEVELS,
        default=PRIORITY_LEVELS.normal
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default=ORDER_STATUS.pending
    )
    
    # Clinical justification (multilingual)
    clinical_justification_en = models.TextField(
        blank=True,
        help_text="Clinical justification in English"
    )
    clinical_justification_ar = models.TextField(
        blank=True,
        help_text="Clinical justification in Arabic"
    )
    
    # Order metadata
    ordered_date = models.DateTimeField(default=timezone.now)
    requested_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Preferred test date/time"
    )
    
    # Integration with Laboratory Module
    lab_reference = models.CharField(
        max_length=50,
        blank=True,
        help_text="Reference from Laboratory Module"
    )
    lab_status = models.CharField(
        max_length=20,
        default='pending',
        help_text="Status from Laboratory Module"
    )
    
    class Meta:
        ordering = ['-ordered_date']
        indexes = [
            models.Index(fields=['consultation']),
            models.Index(fields=['priority']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Lab Order {self.order_code} - {self.test_name_en}"


class LabResult(TimeStampedModel):
    """
    Laboratory test results linked to lab orders.
    """
    
    RESULT_STATUS = Choices(
        ('normal', 'Normal'),
        ('abnormal', 'Abnormal'),
        ('critical', 'Critical'),
        ('pending', 'Pending Review'),
    )
    
    lab_order = models.ForeignKey(
        LabOrder,
        on_delete=models.CASCADE,
        related_name='results'
    )
    
    # Result details
    result_value = models.CharField(
        max_length=200,
        help_text="Test result value"
    )
    reference_range = models.CharField(
        max_length=100,
        blank=True,
        help_text="Normal reference range"
    )
    unit = models.CharField(
        max_length=50,
        blank=True,
        help_text="Measurement unit"
    )
    
    # Result interpretation
    status = models.CharField(
        max_length=20,
        choices=RESULT_STATUS,
        default=RESULT_STATUS.pending
    )
    
    interpretation_en = models.TextField(
        blank=True,
        help_text="Result interpretation in English"
    )
    interpretation_ar = models.TextField(
        blank=True,
        help_text="Result interpretation in Arabic"
    )
    
    # Result metadata
    result_date = models.DateTimeField(default=timezone.now)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Doctor who reviewed the result"
    )
    reviewed_date = models.DateTimeField(
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-result_date']
    
    def __str__(self):
        return f"Result for {self.lab_order.test_name_en} - {self.result_value}"


class Attachment(TimeStampedModel, SoftDeletableModel):
    """
    Medical file attachments linked to consultations.
    Supports various file types with secure storage.
    """
    
    FILE_TYPES = Choices(
        ('image', 'Image'),
        ('document', 'Document'),
        ('lab_result', 'Lab Result'),
        ('xray', 'X-Ray'),
        ('scan', 'Scan'),
        ('report', 'Report'),
        ('other', 'Other'),
    )
    
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    
    # File details
    file = models.FileField(
        upload_to='consultation_attachments/%Y/%m/%d/',
        help_text="Uploaded file"
    )
    file_name = models.CharField(
        max_length=255,
        help_text="Original file name"
    )
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPES,
        help_text="Type of medical file"
    )
    file_size = models.PositiveIntegerField(
        help_text="File size in bytes"
    )
    
    # File metadata (multilingual)
    title_en = models.CharField(
        max_length=200,
        help_text="File title in English"
    )
    title_ar = models.CharField(
        max_length=200,
        help_text="File title in Arabic"
    )
    
    description_en = models.TextField(
        blank=True,
        help_text="File description in English"
    )
    description_ar = models.TextField(
        blank=True,
        help_text="File description in Arabic"
    )
    
    # Security and access
    is_confidential = models.BooleanField(
        default=True,
        help_text="Mark as confidential medical information"
    )
    access_level = models.CharField(
        max_length=20,
        default='doctor_only',
        help_text="Access permission level"
    )
    
    # Audit fields
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='attachments_uploaded'
    )
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['consultation']),
            models.Index(fields=['file_type']),
        ]
    
    def __str__(self):
        return f"{self.title_en} - {self.consultation.consultation_code}"
    
    def get_title(self, language='en'):
        """Get file title in specified language."""
        return getattr(self, f'title_{language}', '')


class FollowUpNote(TimeStampedModel, SoftDeletableModel):
    """
    Follow-up notes and progress updates for consultations.
    Supports future appointment linking.
    """
    
    NOTE_TYPES = Choices(
        ('progress', 'Progress Update'),
        ('follow_up', 'Follow-up Note'),
        ('complication', 'Complication'),
        ('resolution', 'Resolution'),
        ('general', 'General Note'),
    )
    
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='follow_up_notes'
    )
    
    # Note details
    note_type = models.CharField(
        max_length=20,
        choices=NOTE_TYPES,
        default=NOTE_TYPES.general
    )
    
    # Multilingual content
    content_en = models.TextField(
        help_text="Note content in English"
    )
    content_ar = models.TextField(
        help_text="Note content in Arabic"
    )
    
    # Note metadata
    note_date = models.DateTimeField(default=timezone.now)
    is_urgent = models.BooleanField(
        default=False,
        help_text="Mark as urgent for doctor attention"
    )
    
    # Future appointment linking
    linked_appointment_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Reference to future appointment ID"
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='follow_up_notes_created'
    )
    
    class Meta:
        ordering = ['-note_date']
        indexes = [
            models.Index(fields=['consultation']),
            models.Index(fields=['note_type']),
            models.Index(fields=['is_urgent']),
        ]
    
    def __str__(self):
        return f"Follow-up Note - {self.consultation.consultation_code}"
    
    def get_content(self, language='en'):
        """Get note content in specified language."""
        return getattr(self, f'content_{language}', '')


class AuditLog(TimeStampedModel):
    """
    Audit trail for all consultation-related actions.
    Tracks changes for compliance and security.
    """
    
    ACTION_TYPES = Choices(
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('upload', 'Upload'),
        ('download', 'Download'),
    )
    
    # Audit details
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='consultation_audit_logs'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_TYPES
    )
    model_name = models.CharField(
        max_length=100,
        help_text="Django model name"
    )
    object_id = models.CharField(
        max_length=100,
        help_text="Object ID that was modified"
    )
    
    # Change details
    old_values = models.JSONField(
        null=True,
        blank=True,
        help_text="Previous values (for updates)"
    )
    new_values = models.JSONField(
        null=True,
        blank=True,
        help_text="New values"
    )
    
    # Request metadata
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        blank=True
    )
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['model_name']),
            models.Index(fields=['created']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.model_name}"
