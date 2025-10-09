"""
Patient Management Filters

This module provides filtering capabilities for patient management APIs.
"""

import django_filters
from django.db.models import Q
from .models import Patient, MedicalHistory, Allergy, ChronicCondition, PatientDocument


class PatientFilter(django_filters.FilterSet):
    """
    Filter set for Patient model with multilingual search support.
    """
    
    # Basic filters
    patient_code = django_filters.CharFilter(lookup_expr='icontains')
    national_id = django_filters.CharFilter(lookup_expr='exact')
    phone_number = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    
    # Name filters (multilingual)
    first_name = django_filters.CharFilter(method='filter_first_name')
    last_name = django_filters.CharFilter(method='filter_last_name')
    full_name = django_filters.CharFilter(method='filter_full_name')
    
    # Demographics
    gender = django_filters.ChoiceFilter(choices=Patient.GENDER_CHOICES)
    status = django_filters.ChoiceFilter(choices=Patient.STATUS_CHOICES)
    blood_type = django_filters.ChoiceFilter(choices=Patient._meta.get_field('blood_type').choices)
    
    # Age filters
    min_age = django_filters.NumberFilter(method='filter_min_age')
    max_age = django_filters.NumberFilter(method='filter_max_age')
    age_range = django_filters.CharFilter(method='filter_age_range')
    
    # Date filters
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    birth_after = django_filters.DateFilter(field_name='date_of_birth', lookup_expr='gte')
    birth_before = django_filters.DateFilter(field_name='date_of_birth', lookup_expr='lte')
    
    # Location filters
    city = django_filters.CharFilter(lookup_expr='icontains')
    state_province = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='icontains')
    
    # Search filter
    search = django_filters.CharFilter(method='filter_search')
    
    # Soft delete filter
    include_deleted = django_filters.BooleanFilter(method='filter_include_deleted')
    
    class Meta:
        model = Patient
        fields = [
            'patient_code', 'national_id', 'phone_number', 'email',
            'first_name', 'last_name', 'full_name', 'gender', 'status',
            'blood_type', 'min_age', 'max_age', 'age_range', 'created_after',
            'created_before', 'birth_after', 'birth_before', 'city',
            'state_province', 'country', 'search', 'include_deleted'
        ]
    
    def filter_first_name(self, queryset, name, value):
        """Filter by first name in both English and Arabic"""
        return queryset.filter(
            Q(first_name_en__icontains=value) | Q(first_name_ar__icontains=value)
        )
    
    def filter_last_name(self, queryset, name, value):
        """Filter by last name in both English and Arabic"""
        return queryset.filter(
            Q(last_name_en__icontains=value) | Q(last_name_ar__icontains=value)
        )
    
    def filter_full_name(self, queryset, name, value):
        """Filter by full name in both English and Arabic"""
        return queryset.filter(
            Q(first_name_en__icontains=value) | Q(first_name_ar__icontains=value) |
            Q(last_name_en__icontains=value) | Q(last_name_ar__icontains=value) |
            Q(middle_name_en__icontains=value) | Q(middle_name_ar__icontains=value)
        )
    
    def filter_min_age(self, queryset, name, value):
        """Filter by minimum age"""
        from datetime import date
        from django.utils import timezone
        
        today = timezone.now().date()
        max_birth_date = date(today.year - value, today.month, today.day)
        return queryset.filter(date_of_birth__lte=max_birth_date)
    
    def filter_max_age(self, queryset, name, value):
        """Filter by maximum age"""
        from datetime import date
        from django.utils import timezone
        
        today = timezone.now().date()
        min_birth_date = date(today.year - value - 1, today.month, today.day)
        return queryset.filter(date_of_birth__gte=min_birth_date)
    
    def filter_age_range(self, queryset, name, value):
        """Filter by age range (format: min-max)"""
        try:
            min_age, max_age = map(int, value.split('-'))
            from datetime import date
            from django.utils import timezone
            
            today = timezone.now().date()
            max_birth_date = date(today.year - min_age, today.month, today.day)
            min_birth_date = date(today.year - max_age - 1, today.month, today.day)
            
            return queryset.filter(
                date_of_birth__gte=min_birth_date,
                date_of_birth__lte=max_birth_date
            )
        except (ValueError, TypeError):
            return queryset
    
    def filter_search(self, queryset, name, value):
        """Comprehensive search across multiple fields"""
        return queryset.filter(
            Q(patient_code__icontains=value) |
            Q(first_name_en__icontains=value) | Q(first_name_ar__icontains=value) |
            Q(last_name_en__icontains=value) | Q(last_name_ar__icontains=value) |
            Q(middle_name_en__icontains=value) | Q(middle_name_ar__icontains=value) |
            Q(national_id__icontains=value) |
            Q(phone_number__icontains=value) |
            Q(email__icontains=value) |
            Q(address_en__icontains=value) | Q(address_ar__icontains=value) |
            Q(city__icontains=value) |
            Q(emergency_contact_name__icontains=value) |
            Q(notes__icontains=value)
        )
    
    def filter_include_deleted(self, queryset, name, value):
        """Include or exclude soft-deleted records"""
        if value:
            return queryset  # Include all records
        else:
            return queryset.filter(is_deleted=False)  # Exclude deleted records


class MedicalHistoryFilter(django_filters.FilterSet):
    """
    Filter set for MedicalHistory model.
    """
    
    patient = django_filters.NumberFilter(field_name='patient__id')
    patient_code = django_filters.CharFilter(field_name='patient__patient_code', lookup_expr='icontains')
    category = django_filters.ChoiceFilter(choices=MedicalHistory.CATEGORY_CHOICES)
    
    # Title and description filters (multilingual)
    title = django_filters.CharFilter(method='filter_title')
    description = django_filters.CharFilter(method='filter_description')
    
    # Date filters
    event_date_after = django_filters.DateFilter(field_name='event_date', lookup_expr='gte')
    event_date_before = django_filters.DateFilter(field_name='event_date', lookup_expr='lte')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Search filter
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = MedicalHistory
        fields = [
            'patient', 'patient_code', 'category', 'title', 'description',
            'event_date_after', 'event_date_before', 'created_after',
            'created_before', 'search'
        ]
    
    def filter_title(self, queryset, name, value):
        """Filter by title in both English and Arabic"""
        return queryset.filter(
            Q(title_en__icontains=value) | Q(title_ar__icontains=value)
        )
    
    def filter_description(self, queryset, name, value):
        """Filter by description in both English and Arabic"""
        return queryset.filter(
            Q(description_en__icontains=value) | Q(description_ar__icontains=value)
        )
    
    def filter_search(self, queryset, name, value):
        """Comprehensive search across multiple fields"""
        return queryset.filter(
            Q(title_en__icontains=value) | Q(title_ar__icontains=value) |
            Q(description_en__icontains=value) | Q(description_ar__icontains=value) |
            Q(diagnosis_code__icontains=value) |
            Q(treatment_notes__icontains=value)
        )


class AllergyFilter(django_filters.FilterSet):
    """
    Filter set for Allergy model.
    """
    
    patient = django_filters.NumberFilter(field_name='patient__id')
    patient_code = django_filters.CharFilter(field_name='patient__patient_code', lookup_expr='icontains')
    allergy_type = django_filters.ChoiceFilter(choices=Allergy.ALLERGY_TYPE_CHOICES)
    severity = django_filters.ChoiceFilter(choices=Allergy.SEVERITY_CHOICES)
    
    # Allergen filters (multilingual)
    allergen = django_filters.CharFilter(method='filter_allergen')
    description = django_filters.CharFilter(method='filter_description')
    
    # Date filters
    first_occurrence_after = django_filters.DateFilter(field_name='first_occurrence', lookup_expr='gte')
    first_occurrence_before = django_filters.DateFilter(field_name='first_occurrence', lookup_expr='lte')
    last_occurrence_after = django_filters.DateFilter(field_name='last_occurrence', lookup_expr='gte')
    last_occurrence_before = django_filters.DateFilter(field_name='last_occurrence', lookup_expr='lte')
    
    # Search filter
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Allergy
        fields = [
            'patient', 'patient_code', 'allergy_type', 'severity', 'allergen',
            'description', 'first_occurrence_after', 'first_occurrence_before',
            'last_occurrence_after', 'last_occurrence_before', 'search'
        ]
    
    def filter_allergen(self, queryset, name, value):
        """Filter by allergen in both English and Arabic"""
        return queryset.filter(
            Q(allergen_en__icontains=value) | Q(allergen_ar__icontains=value)
        )
    
    def filter_description(self, queryset, name, value):
        """Filter by description in both English and Arabic"""
        return queryset.filter(
            Q(description_en__icontains=value) | Q(description_ar__icontains=value)
        )
    
    def filter_search(self, queryset, name, value):
        """Comprehensive search across multiple fields"""
        return queryset.filter(
            Q(allergen_en__icontains=value) | Q(allergen_ar__icontains=value) |
            Q(description_en__icontains=value) | Q(description_ar__icontains=value) |
            Q(symptoms__icontains=value) |
            Q(treatment_notes__icontains=value)
        )


class ChronicConditionFilter(django_filters.FilterSet):
    """
    Filter set for ChronicCondition model.
    """
    
    patient = django_filters.NumberFilter(field_name='patient__id')
    patient_code = django_filters.CharFilter(field_name='patient__patient_code', lookup_expr='icontains')
    condition_type = django_filters.ChoiceFilter(choices=ChronicCondition.CONDITION_TYPE_CHOICES)
    severity = django_filters.ChoiceFilter(choices=ChronicCondition.SEVERITY_CHOICES)
    is_active = django_filters.BooleanFilter()
    
    # Condition name filters (multilingual)
    condition_name = django_filters.CharFilter(method='filter_condition_name')
    description = django_filters.CharFilter(method='filter_description')
    
    # Date filters
    diagnosis_date_after = django_filters.DateFilter(field_name='diagnosis_date', lookup_expr='gte')
    diagnosis_date_before = django_filters.DateFilter(field_name='diagnosis_date', lookup_expr='lte')
    last_review_after = django_filters.DateFilter(field_name='last_review_date', lookup_expr='gte')
    last_review_before = django_filters.DateFilter(field_name='last_review_date', lookup_expr='lte')
    
    # Search filter
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = ChronicCondition
        fields = [
            'patient', 'patient_code', 'condition_type', 'severity', 'is_active',
            'condition_name', 'description', 'diagnosis_date_after', 'diagnosis_date_before',
            'last_review_after', 'last_review_before', 'search'
        ]
    
    def filter_condition_name(self, queryset, name, value):
        """Filter by condition name in both English and Arabic"""
        return queryset.filter(
            Q(condition_name_en__icontains=value) | Q(condition_name_ar__icontains=value)
        )
    
    def filter_description(self, queryset, name, value):
        """Filter by description in both English and Arabic"""
        return queryset.filter(
            Q(description_en__icontains=value) | Q(description_ar__icontains=value)
        )
    
    def filter_search(self, queryset, name, value):
        """Comprehensive search across multiple fields"""
        return queryset.filter(
            Q(condition_name_en__icontains=value) | Q(condition_name_ar__icontains=value) |
            Q(description_en__icontains=value) | Q(description_ar__icontains=value) |
            Q(icd_code__icontains=value) |
            Q(current_medications__icontains=value) |
            Q(management_plan__icontains=value) |
            Q(notes__icontains=value)
        )


class PatientDocumentFilter(django_filters.FilterSet):
    """
    Filter set for PatientDocument model.
    """
    
    patient = django_filters.NumberFilter(field_name='patient__id')
    patient_code = django_filters.CharFilter(field_name='patient__patient_code', lookup_expr='icontains')
    document_type = django_filters.ChoiceFilter(choices=PatientDocument.DOCUMENT_TYPE_CHOICES)
    is_verified = django_filters.BooleanFilter()
    
    # Title and description filters (multilingual)
    title = django_filters.CharFilter(method='filter_title')
    description = django_filters.CharFilter(method='filter_description')
    
    # Date filters
    upload_date_after = django_filters.DateFilter(field_name='upload_date', lookup_expr='gte')
    upload_date_before = django_filters.DateFilter(field_name='upload_date', lookup_expr='lte')
    document_date_after = django_filters.DateFilter(field_name='document_date', lookup_expr='gte')
    document_date_before = django_filters.DateFilter(field_name='document_date', lookup_expr='lte')
    
    # File filters
    file_extension = django_filters.CharFilter(lookup_expr='exact')
    min_file_size = django_filters.NumberFilter(field_name='file_size', lookup_expr='gte')
    max_file_size = django_filters.NumberFilter(field_name='file_size', lookup_expr='lte')
    
    # Search filter
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = PatientDocument
        fields = [
            'patient', 'patient_code', 'document_type', 'is_verified', 'title',
            'description', 'upload_date_after', 'upload_date_before',
            'document_date_after', 'document_date_before', 'file_extension',
            'min_file_size', 'max_file_size', 'search'
        ]
    
    def filter_title(self, queryset, name, value):
        """Filter by title in both English and Arabic"""
        return queryset.filter(
            Q(title_en__icontains=value) | Q(title_ar__icontains=value)
        )
    
    def filter_description(self, queryset, name, value):
        """Filter by description in both English and Arabic"""
        return queryset.filter(
            Q(description_en__icontains=value) | Q(description_ar__icontains=value)
        )
    
    def filter_search(self, queryset, name, value):
        """Comprehensive search across multiple fields"""
        return queryset.filter(
            Q(title_en__icontains=value) | Q(title_ar__icontains=value) |
            Q(description_en__icontains=value) | Q(description_ar__icontains=value)
        )
