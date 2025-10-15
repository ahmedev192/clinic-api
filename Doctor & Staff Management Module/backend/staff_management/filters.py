"""
Custom filters for Staff Management
"""

import django_filters
from django.db.models import Q
from .models import Staff, Doctor, Schedule


class StaffFilter(django_filters.FilterSet):
    """
    Filter for Staff model
    """
    role = django_filters.CharFilter(field_name='role__code')
    employment_status = django_filters.ChoiceFilter(choices=Staff.EMPLOYMENT_STATUS_CHOICES)
    gender = django_filters.ChoiceFilter(choices=Staff.GENDER_CHOICES)
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='country', lookup_expr='icontains')
    joining_date_from = django_filters.DateFilter(field_name='joining_date', lookup_expr='gte')
    joining_date_to = django_filters.DateFilter(field_name='joining_date', lookup_expr='lte')
    has_profile_image = django_filters.BooleanFilter(field_name='profile_image', lookup_expr='isnull')
    
    # Search across multiple fields
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Staff
        fields = {
            'staff_id': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'phone_primary': ['exact', 'icontains'],
            'national_id': ['exact', 'icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(first_name_en__icontains=value) |
            Q(last_name_en__icontains=value) |
            Q(first_name_ar__icontains=value) |
            Q(last_name_ar__icontains=value) |
            Q(email__icontains=value) |
            Q(staff_id__icontains=value) |
            Q(national_id__icontains=value)
        )


class DoctorFilter(django_filters.FilterSet):
    """
    Filter for Doctor model
    """
    specialization = django_filters.CharFilter(field_name='specializations__name_en', lookup_expr='icontains')
    specialization_id = django_filters.NumberFilter(field_name='specializations__id')
    years_experience_min = django_filters.NumberFilter(field_name='years_of_experience', lookup_expr='gte')
    years_experience_max = django_filters.NumberFilter(field_name='years_of_experience', lookup_expr='lte')
    is_available = django_filters.BooleanFilter(field_name='is_available')
    is_accepting_new_patients = django_filters.BooleanFilter(field_name='is_accepting_new_patients')
    consultation_fee_min = django_filters.NumberFilter(field_name='consultation_fee', lookup_expr='gte')
    consultation_fee_max = django_filters.NumberFilter(field_name='consultation_fee', lookup_expr='lte')
    language = django_filters.CharFilter(method='filter_language')
    
    # Search across multiple fields
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Doctor
        fields = {
            'medical_license_number': ['exact', 'icontains'],
            'professional_title_en': ['icontains'],
            'professional_title_ar': ['icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(staff__first_name_en__icontains=value) |
            Q(staff__last_name_en__icontains=value) |
            Q(staff__first_name_ar__icontains=value) |
            Q(staff__last_name_ar__icontains=value) |
            Q(medical_license_number__icontains=value) |
            Q(professional_title_en__icontains=value) |
            Q(professional_title_ar__icontains=value)
        )
    
    def filter_language(self, queryset, name, value):
        """
        Filter by language spoken
        """
        if not value:
            return queryset
        
        return queryset.filter(languages__icontains=value)


class ScheduleFilter(django_filters.FilterSet):
    """
    Filter for Schedule model
    """
    staff_id = django_filters.NumberFilter(field_name='staff__id')
    staff_name = django_filters.CharFilter(method='filter_staff_name')
    day_of_week = django_filters.ChoiceFilter(choices=Schedule.DAY_CHOICES)
    is_active = django_filters.BooleanFilter(field_name='is_active')
    time_from = django_filters.TimeFilter(field_name='start_time', lookup_expr='gte')
    time_to = django_filters.TimeFilter(field_name='end_time', lookup_expr='lte')
    
    class Meta:
        model = Schedule
        fields = ['staff', 'day_of_week', 'is_active']
    
    def filter_staff_name(self, queryset, name, value):
        """
        Filter by staff name
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(staff__first_name_en__icontains=value) |
            Q(staff__last_name_en__icontains=value) |
            Q(staff__first_name_ar__icontains=value) |
            Q(staff__last_name_ar__icontains=value)
        )
