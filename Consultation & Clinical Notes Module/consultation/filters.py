"""
Django Filter classes for the Consultation & Clinical Notes Module.
Provides filtering capabilities for all API endpoints.
"""

import django_filters
from django.db.models import Q
from .models import Consultation, Diagnosis, Prescription, LabOrder, Attachment, FollowUpNote


class ConsultationFilter(django_filters.FilterSet):
    """Filter for Consultation model."""
    
    patient_id = django_filters.NumberFilter(field_name='patient_id')
    doctor_id = django_filters.NumberFilter(field_name='doctor_id')
    appointment_id = django_filters.NumberFilter(field_name='appointment_id')
    consultation_type = django_filters.ChoiceFilter(choices=Consultation.CONSULTATION_TYPES)
    status = django_filters.ChoiceFilter(choices=Consultation.STATUS_CHOICES)
    
    # Date range filters
    consultation_date_from = django_filters.DateTimeFilter(
        field_name='consultation_date',
        lookup_expr='gte'
    )
    consultation_date_to = django_filters.DateTimeFilter(
        field_name='consultation_date',
        lookup_expr='lte'
    )
    
    # Duration filters
    duration_min = django_filters.NumberFilter(
        field_name='duration_minutes',
        lookup_expr='gte'
    )
    duration_max = django_filters.NumberFilter(
        field_name='duration_minutes',
        lookup_expr='lte'
    )
    
    # Multilingual text search
    search_text = django_filters.CharFilter(method='filter_search_text')
    
    class Meta:
        model = Consultation
        fields = [
            'patient_id', 'doctor_id', 'appointment_id', 'consultation_type',
            'status', 'consultation_date_from', 'consultation_date_to',
            'duration_min', 'duration_max', 'search_text'
        ]
    
    def filter_search_text(self, queryset, name, value):
        """Search across multilingual text fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(consultation_code__icontains=value) |
            Q(chief_complaint_en__icontains=value) |
            Q(chief_complaint_ar__icontains=value) |
            Q(symptoms_en__icontains=value) |
            Q(symptoms_ar__icontains=value) |
            Q(examination_findings_en__icontains=value) |
            Q(examination_findings_ar__icontains=value) |
            Q(assessment_notes_en__icontains=value) |
            Q(assessment_notes_ar__icontains=value)
        )


class DiagnosisFilter(django_filters.FilterSet):
    """Filter for Diagnosis model."""
    
    category = django_filters.CharFilter(field_name='category', lookup_expr='icontains')
    is_chronic = django_filters.BooleanFilter(field_name='is_chronic')
    is_contagious = django_filters.BooleanFilter(field_name='is_contagious')
    severity_level = django_filters.ChoiceFilter(choices=Diagnosis.SEVERITY_LEVELS)
    
    # Multilingual text search
    search_text = django_filters.CharFilter(method='filter_search_text')
    
    class Meta:
        model = Diagnosis
        fields = ['category', 'is_chronic', 'is_contagious', 'severity_level', 'search_text']
    
    def filter_search_text(self, queryset, name, value):
        """Search across multilingual text fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(diagnosis_code__icontains=value) |
            Q(name_en__icontains=value) |
            Q(name_ar__icontains=value) |
            Q(description_en__icontains=value) |
            Q(description_ar__icontains=value) |
            Q(category__icontains=value)
        )


class PrescriptionFilter(django_filters.FilterSet):
    """Filter for Prescription model."""
    
    consultation_id = django_filters.UUIDFilter(field_name='consultation_id')
    status = django_filters.ChoiceFilter(choices=Prescription.PRESCRIPTION_STATUS)
    pharmacy_status = django_filters.CharFilter(field_name='pharmacy_status')
    
    # Date range filters
    prescribed_date_from = django_filters.DateTimeFilter(
        field_name='prescribed_date',
        lookup_expr='gte'
    )
    prescribed_date_to = django_filters.DateTimeFilter(
        field_name='prescribed_date',
        lookup_expr='lte'
    )
    
    # Validity filters
    valid_until_from = django_filters.DateFilter(
        field_name='valid_until',
        lookup_expr='gte'
    )
    valid_until_to = django_filters.DateFilter(
        field_name='valid_until',
        lookup_expr='lte'
    )
    
    # Multilingual text search
    search_text = django_filters.CharFilter(method='filter_search_text')
    
    class Meta:
        model = Prescription
        fields = [
            'consultation_id', 'status', 'pharmacy_status',
            'prescribed_date_from', 'prescribed_date_to',
            'valid_until_from', 'valid_until_to', 'search_text'
        ]
    
    def filter_search_text(self, queryset, name, value):
        """Search across multilingual text fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(prescription_code__icontains=value) |
            Q(notes_en__icontains=value) |
            Q(notes_ar__icontains=value) |
            Q(pharmacy_notes__icontains=value)
        )


class LabOrderFilter(django_filters.FilterSet):
    """Filter for LabOrder model."""
    
    consultation_id = django_filters.UUIDFilter(field_name='consultation_id')
    test_category = django_filters.CharFilter(field_name='test_category', lookup_expr='icontains')
    priority = django_filters.ChoiceFilter(choices=LabOrder.PRIORITY_LEVELS)
    status = django_filters.ChoiceFilter(choices=LabOrder.ORDER_STATUS)
    lab_status = django_filters.CharFilter(field_name='lab_status')
    
    # Date range filters
    ordered_date_from = django_filters.DateTimeFilter(
        field_name='ordered_date',
        lookup_expr='gte'
    )
    ordered_date_to = django_filters.DateTimeFilter(
        field_name='ordered_date',
        lookup_expr='lte'
    )
    
    requested_date_from = django_filters.DateTimeFilter(
        field_name='requested_date',
        lookup_expr='gte'
    )
    requested_date_to = django_filters.DateTimeFilter(
        field_name='requested_date',
        lookup_expr='lte'
    )
    
    # Multilingual text search
    search_text = django_filters.CharFilter(method='filter_search_text')
    
    class Meta:
        model = LabOrder
        fields = [
            'consultation_id', 'test_category', 'priority', 'status', 'lab_status',
            'ordered_date_from', 'ordered_date_to',
            'requested_date_from', 'requested_date_to', 'search_text'
        ]
    
    def filter_search_text(self, queryset, name, value):
        """Search across multilingual text fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(order_code__icontains=value) |
            Q(test_name_en__icontains=value) |
            Q(test_name_ar__icontains=value) |
            Q(test_category__icontains=value) |
            Q(clinical_justification_en__icontains=value) |
            Q(clinical_justification_ar__icontains=value) |
            Q(lab_reference__icontains=value)
        )


class AttachmentFilter(django_filters.FilterSet):
    """Filter for Attachment model."""
    
    consultation_id = django_filters.UUIDFilter(field_name='consultation_id')
    file_type = django_filters.ChoiceFilter(choices=Attachment.FILE_TYPES)
    is_confidential = django_filters.BooleanFilter(field_name='is_confidential')
    access_level = django_filters.CharFilter(field_name='access_level')
    uploaded_by = django_filters.NumberFilter(field_name='uploaded_by')
    
    # File size filters
    file_size_min = django_filters.NumberFilter(
        field_name='file_size',
        lookup_expr='gte'
    )
    file_size_max = django_filters.NumberFilter(
        field_name='file_size',
        lookup_expr='lte'
    )
    
    # Date range filters
    uploaded_date_from = django_filters.DateTimeFilter(
        field_name='created',
        lookup_expr='gte'
    )
    uploaded_date_to = django_filters.DateTimeFilter(
        field_name='created',
        lookup_expr='lte'
    )
    
    # Multilingual text search
    search_text = django_filters.CharFilter(method='filter_search_text')
    
    class Meta:
        model = Attachment
        fields = [
            'consultation_id', 'file_type', 'is_confidential', 'access_level',
            'uploaded_by', 'file_size_min', 'file_size_max',
            'uploaded_date_from', 'uploaded_date_to', 'search_text'
        ]
    
    def filter_search_text(self, queryset, name, value):
        """Search across multilingual text fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(file_name__icontains=value) |
            Q(title_en__icontains=value) |
            Q(title_ar__icontains=value) |
            Q(description_en__icontains=value) |
            Q(description_ar__icontains=value)
        )


class FollowUpNoteFilter(django_filters.FilterSet):
    """Filter for FollowUpNote model."""
    
    consultation_id = django_filters.UUIDFilter(field_name='consultation_id')
    note_type = django_filters.ChoiceFilter(choices=FollowUpNote.NOTE_TYPES)
    is_urgent = django_filters.BooleanFilter(field_name='is_urgent')
    created_by = django_filters.NumberFilter(field_name='created_by')
    linked_appointment_id = django_filters.NumberFilter(field_name='linked_appointment_id')
    
    # Date range filters
    note_date_from = django_filters.DateTimeFilter(
        field_name='note_date',
        lookup_expr='gte'
    )
    note_date_to = django_filters.DateTimeFilter(
        field_name='note_date',
        lookup_expr='lte'
    )
    
    # Multilingual text search
    search_text = django_filters.CharFilter(method='filter_search_text')
    
    class Meta:
        model = FollowUpNote
        fields = [
            'consultation_id', 'note_type', 'is_urgent', 'created_by',
            'linked_appointment_id', 'note_date_from', 'note_date_to', 'search_text'
        ]
    
    def filter_search_text(self, queryset, name, value):
        """Search across multilingual text fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(content_en__icontains=value) |
            Q(content_ar__icontains=value)
        )
