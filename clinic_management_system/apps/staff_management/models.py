"""
Staff Management Models for Clinic Management System
Supports bilingual operation (Arabic + English)
"""

from django.db import models
from apps.accounts.models import User
from django.contrib.auth.models import Group
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel, SoftDeletableModel
from django.core.exceptions import ValidationError
import uuid


class BilingualTextField(models.TextField):
    """Custom field for storing bilingual text (English + Arabic)"""
    def __init__(self, *args, **kwargs):
        kwargs['help_text'] = kwargs.get('help_text', '') + ' (English/Arabic)'
        super().__init__(*args, **kwargs)


class BilingualCharField(models.CharField):
    """Custom field for storing bilingual text (English + Arabic)"""
    def __init__(self, *args, **kwargs):
        kwargs['help_text'] = kwargs.get('help_text', '') + ' (English/Arabic)'
        super().__init__(*args, **kwargs)


class Role(TimeStampedModel, SoftDeletableModel):
    """
    Staff roles with permissions
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
        ('pharmacist', 'Pharmacist'),
        ('lab_technician', 'Lab Technician'),
        ('technician', 'Technician'),
        ('manager', 'Manager'),
    ]
    
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique role code (e.g., 'ADMIN', 'DOC')"
    )
    name_en = models.CharField(max_length=100, verbose_name="Role Name (English)")
    name_ar = models.CharField(max_length=100, verbose_name="Role Name (Arabic)")
    description_en = models.TextField(blank=True, verbose_name="Description (English)")
    description_ar = models.TextField(blank=True, verbose_name="Description (Arabic)")
    permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        help_text="Specific permissions for this role"
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name_en']
        verbose_name = "Role"
        verbose_name_plural = "Roles"
    
    def __str__(self):
        return f"{self.name_en} ({self.code})"
    
    def clean(self):
        if not self.code:
            raise ValidationError("Role code is required")
        self.code = self.code.upper()


class Specialization(TimeStampedModel, SoftDeletableModel):
    """
    Medical specializations for doctors
    """
    name_en = models.CharField(max_length=100, verbose_name="Specialization (English)")
    name_ar = models.CharField(max_length=100, verbose_name="Specialization (Arabic)")
    description_en = models.TextField(blank=True, verbose_name="Description (English)")
    description_ar = models.TextField(blank=True, verbose_name="Description (Arabic)")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name_en']
        verbose_name = "Specialization"
        verbose_name_plural = "Specializations"
    
    def __str__(self):
        return f"{self.name_en}"


class Staff(TimeStampedModel, SoftDeletableModel):
    """
    Base staff model with common fields
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]
    
    # Unique identifiers
    staff_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique staff identifier (e.g., 'STAFF001')"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile',
        help_text="Linked Django user account"
    )
    
    # Personal information
    first_name_en = models.CharField(max_length=50, verbose_name="First Name (English)")
    first_name_ar = models.CharField(max_length=50, verbose_name="First Name (Arabic)")
    last_name_en = models.CharField(max_length=50, verbose_name="Last Name (English)")
    last_name_ar = models.CharField(max_length=50, verbose_name="Last Name (Arabic)")
    middle_name_en = models.CharField(max_length=50, blank=True, verbose_name="Middle Name (English)")
    middle_name_ar = models.CharField(max_length=50, blank=True, verbose_name="Middle Name (Arabic)")
    
    # Contact information
    email = models.EmailField(unique=True)
    phone_primary = models.CharField(max_length=20)
    phone_secondary = models.CharField(max_length=20, blank=True)
    address_en = models.TextField(verbose_name="Address (English)")
    address_ar = models.TextField(verbose_name="Address (Arabic)")
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Saudi Arabia")
    
    # Personal details
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    national_id = models.CharField(max_length=20, unique=True)
    passport_number = models.CharField(max_length=20, blank=True)
    
    # Employment details
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='staff')
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='active'
    )
    joining_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    
    # Profile image
    profile_image = models.ImageField(
        upload_to='staff_profiles/',
        null=True,
        blank=True,
        help_text="Profile picture"
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_staff'
    )
    
    class Meta:
        ordering = ['first_name_en', 'last_name_en']
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
    
    def __str__(self):
        return f"{self.first_name_en} {self.last_name_en} ({self.staff_id})"
    
    @property
    def full_name_en(self):
        return f"{self.first_name_en} {self.last_name_en}"
    
    @property
    def full_name_ar(self):
        return f"{self.first_name_ar} {self.last_name_ar}"
    
    def clean(self):
        if not self.staff_id:
            # Generate staff ID if not provided
            self.staff_id = self.generate_staff_id()
    
    def generate_staff_id(self):
        """Generate unique staff ID based on role"""
        role_prefix = self.role.code[:3] if self.role else 'STF'
        last_staff = Staff.objects.filter(
            staff_id__startswith=role_prefix
        ).order_by('staff_id').last()
        
        if last_staff:
            try:
                last_number = int(last_staff.staff_id[3:])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{role_prefix}{new_number:04d}"


class Doctor(TimeStampedModel, SoftDeletableModel):
    """
    Extended model for doctors with medical-specific fields
    """
    staff = models.OneToOneField(
        Staff,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        limit_choices_to={'role__code__in': ['DOC', 'DOCTOR']}
    )
    
    # Medical credentials
    medical_license_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Official medical license number"
    )
    professional_title_en = models.CharField(
        max_length=100,
        verbose_name="Professional Title (English)"
    )
    professional_title_ar = models.CharField(
        max_length=100,
        verbose_name="Professional Title (Arabic)"
    )
    
    # Specializations
    specializations = models.ManyToManyField(
        Specialization,
        related_name='doctors',
        help_text="Medical specializations"
    )
    
    # Experience and qualifications
    years_of_experience = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Years of medical experience"
    )
    biography_en = models.TextField(
        blank=True,
        verbose_name="Biography (English)",
        help_text="Professional biography"
    )
    biography_ar = models.TextField(
        blank=True,
        verbose_name="Biography (Arabic)",
        help_text="Professional biography"
    )
    
    # Languages spoken
    languages = models.JSONField(
        default=list,
        help_text="List of languages spoken (e.g., ['English', 'Arabic'])"
    )
    
    # Financial information
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Standard consultation fee"
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Hourly rate for services"
    )
    
    # Status
    is_available = models.BooleanField(default=True)
    is_accepting_new_patients = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['staff__first_name_en']
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
    
    def __str__(self):
        return f"Dr. {self.staff.full_name_en}"
    
    @property
    def full_name(self):
        """Get full name in English"""
        return self.staff.full_name_en
    
    @property
    def full_name_ar(self):
        """Get full name in Arabic"""
        return self.staff.full_name_ar
    
    @property
    def specializations_display(self):
        return ", ".join([spec.name_en for spec in self.specializations.all()])


class Schedule(TimeStampedModel, SoftDeletableModel):
    """
    Staff working schedules
    """
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Additional notes about this schedule")
    
    class Meta:
        ordering = ['staff', 'day_of_week', 'start_time']
        unique_together = ['staff', 'day_of_week', 'start_time']
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"
    
    def __str__(self):
        return f"{self.staff.full_name_en} - {self.get_day_of_week_display()}"
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time")


class Compensation(TimeStampedModel, SoftDeletableModel):
    """
    Staff compensation tracking
    """
    COMPENSATION_TYPE_CHOICES = [
        ('salary', 'Fixed Salary'),
        ('commission', 'Commission Only'),
        ('mixed', 'Salary + Commission'),
    ]
    
    staff = models.OneToOneField(
        Staff,
        on_delete=models.CASCADE,
        related_name='compensation'
    )
    compensation_type = models.CharField(
        max_length=20,
        choices=COMPENSATION_TYPE_CHOICES,
        default='salary'
    )
    
    # Salary information
    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monthly base salary"
    )
    
    # Commission information
    commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Commission percentage (0-100)"
    )
    commission_per_appointment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Fixed commission per appointment"
    )
    
    # Effective dates
    effective_from = models.DateField()
    effective_until = models.DateField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True, help_text="Additional compensation notes")
    
    class Meta:
        ordering = ['staff', '-effective_from']
        verbose_name = "Compensation"
        verbose_name_plural = "Compensations"
    
    def __str__(self):
        return f"{self.staff.full_name_en} - {self.get_compensation_type_display()}"
    
    def clean(self):
        if self.compensation_type == 'salary' and not self.base_salary:
            raise ValidationError("Base salary is required for salary-based compensation")
        if self.compensation_type in ['commission', 'mixed'] and not any([
            self.commission_percentage, self.commission_per_appointment
        ]):
            raise ValidationError("Commission details are required for commission-based compensation")


class StaffAuditLog(TimeStampedModel):
    """
    Audit log for staff changes
    """
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('status_changed', 'Status Changed'),
        ('role_changed', 'Role Changed'),
        ('schedule_changed', 'Schedule Changed'),
    ]
    
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    field_name = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created']
        verbose_name = "Staff Audit Log"
        verbose_name_plural = "Staff Audit Logs"
    
    def __str__(self):
        return f"{self.staff.full_name_en} - {self.get_action_display()}"
