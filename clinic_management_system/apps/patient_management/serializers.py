"""
Patient Management Serializers

This module provides DRF serializers for all patient management models.
Includes multilingual support and comprehensive validation.
"""

from rest_framework import serializers
from apps.accounts.models import User
from .models import (
    Patient, MedicalHistory, Allergy, ChronicCondition, 
    PatientDocument, PatientSearchLog
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        """Get user's full name"""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model with multilingual support"""
    
    # Computed fields
    full_name = serializers.SerializerMethodField()
    full_name_ar = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'patient_code', 'first_name_en', 'first_name_ar', 'last_name_en', 
            'last_name_ar', 'middle_name_en', 'middle_name_ar', 'full_name', 
            'full_name_ar', 'gender', 'date_of_birth', 'age', 'phone_number', 
            'secondary_phone', 'email', 'address_en', 'address_ar', 'city', 
            'state_province', 'postal_code', 'country', 'national_id', 
            'passport_number', 'blood_type', 'emergency_contact_name', 
            'emergency_contact_phone', 'emergency_contact_relationship', 
            'status', 'notes', 'created_at', 'updated_at', 'created_by', 
            'created_by_name', 'updated_by', 'updated_by_name', 'is_deleted', 
            'deleted_at', 'deleted_by'
        ]
        read_only_fields = [
            'id', 'patient_code', 'created_at', 'updated_at', 'created_by', 
            'created_by_name', 'updated_by', 'updated_by_name', 'is_deleted', 
            'deleted_at', 'deleted_by'
        ]
    
    def get_full_name(self, obj):
        """Get full name in English"""
        return obj.get_full_name()
    
    def get_full_name_ar(self, obj):
        """Get full name in Arabic"""
        return obj.get_full_name_ar()
    
    def get_age(self, obj):
        """Get patient's age"""
        return obj.get_age()
    
    def validate_national_id(self, value):
        """Validate national ID format"""
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("National ID must be exactly 10 digits")
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number uniqueness"""
        if self.instance and self.instance.phone_number == value:
            return value
        
        if Patient.objects.filter(phone_number=value, is_deleted=False).exists():
            raise serializers.ValidationError("A patient with this phone number already exists")
        return value
    
    def validate_national_id(self, value):
        """Validate national ID uniqueness"""
        if self.instance and self.instance.national_id == value:
            return value
        
        if Patient.objects.filter(national_id=value, is_deleted=False).exists():
            raise serializers.ValidationError("A patient with this National ID already exists")
        return value


class PatientListSerializer(serializers.ModelSerializer):
    """Simplified serializer for patient lists"""
    
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'patient_code', 'full_name', 'gender', 'age', 
            'phone_number', 'email', 'status', 'created_at'
        ]
    
    def get_full_name(self, obj):
        """Get full name in English"""
        return obj.get_full_name()
    
    def get_age(self, obj):
        """Get patient's age"""
        return obj.get_age()


class MedicalHistorySerializer(serializers.ModelSerializer):
    """Serializer for MedicalHistory model"""
    
    patient_code = serializers.CharField(source='patient.patient_code', read_only=True)
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = MedicalHistory
        fields = [
            'id', 'patient', 'patient_code', 'patient_name', 'category', 
            'title_en', 'title_ar', 'description_en', 'description_ar', 
            'diagnosis_code', 'treatment_notes', 'event_date', 'created_at', 
            'updated_at', 'created_by', 'created_by_name', 'updated_by', 'updated_by_name'
        ]
        read_only_fields = [
            'id', 'patient_code', 'patient_name', 'created_at', 'updated_at', 
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name'
        ]


class AllergySerializer(serializers.ModelSerializer):
    """Serializer for Allergy model"""
    
    patient_code = serializers.CharField(source='patient.patient_code', read_only=True)
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = Allergy
        fields = [
            'id', 'patient', 'patient_code', 'patient_name', 'allergy_type', 
            'allergen_en', 'allergen_ar', 'description_en', 'description_ar', 
            'severity', 'symptoms', 'treatment_notes', 'first_occurrence', 
            'last_occurrence', 'created_at', 'updated_at', 'created_by', 
            'created_by_name', 'updated_by', 'updated_by_name'
        ]
        read_only_fields = [
            'id', 'patient_code', 'patient_name', 'created_at', 'updated_at', 
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name'
        ]


class ChronicConditionSerializer(serializers.ModelSerializer):
    """Serializer for ChronicCondition model"""
    
    patient_code = serializers.CharField(source='patient.patient_code', read_only=True)
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = ChronicCondition
        fields = [
            'id', 'patient', 'patient_code', 'patient_name', 'condition_type', 
            'condition_name_en', 'condition_name_ar', 'description_en', 
            'description_ar', 'severity', 'diagnosis_date', 'icd_code', 
            'current_medications', 'management_plan', 'notes', 'is_active', 
            'last_review_date', 'created_at', 'updated_at', 'created_by', 
            'created_by_name', 'updated_by', 'updated_by_name'
        ]
        read_only_fields = [
            'id', 'patient_code', 'patient_name', 'created_at', 'updated_at', 
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name'
        ]


class PatientDocumentSerializer(serializers.ModelSerializer):
    """Serializer for PatientDocument model"""
    
    patient_code = serializers.CharField(source='patient.patient_code', read_only=True)
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.username', read_only=True)
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientDocument
        fields = [
            'id', 'patient', 'patient_code', 'patient_name', 'document_type', 
            'title_en', 'title_ar', 'description_en', 'description_ar', 
            'file', 'file_size', 'file_size_display', 'file_extension', 
            'upload_date', 'uploaded_by', 'uploaded_by_name', 'document_date', 
            'is_verified', 'verified_by', 'verified_by_name', 'verified_at'
        ]
        read_only_fields = [
            'id', 'patient_code', 'patient_name', 'file_size', 'file_size_display', 
            'file_extension', 'upload_date', 'uploaded_by', 'uploaded_by_name', 
            'verified_by', 'verified_by_name', 'verified_at'
        ]
    
    def get_file_size_display(self, obj):
        """Get human-readable file size"""
        return obj.get_file_size_display()


class PatientSearchLogSerializer(serializers.ModelSerializer):
    """Serializer for PatientSearchLog model"""
    
    searcher_name = serializers.CharField(source='searcher.username', read_only=True)
    
    class Meta:
        model = PatientSearchLog
        fields = [
            'id', 'searcher', 'searcher_name', 'search_query', 'search_filters', 
            'results_count', 'search_timestamp'
        ]
        read_only_fields = fields


class PatientDetailSerializer(PatientSerializer):
    """Detailed serializer for patient with related data"""
    
    medical_history = MedicalHistorySerializer(many=True, read_only=True)
    allergies = AllergySerializer(many=True, read_only=True)
    chronic_conditions = ChronicConditionSerializer(many=True, read_only=True)
    documents = PatientDocumentSerializer(many=True, read_only=True)
    
    class Meta(PatientSerializer.Meta):
        fields = PatientSerializer.Meta.fields + [
            'medical_history', 'allergies', 'chronic_conditions', 'documents'
        ]


class PatientCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new patients"""
    
    class Meta:
        model = Patient
        fields = [
            'first_name_en', 'first_name_ar', 'last_name_en', 'last_name_ar', 
            'middle_name_en', 'middle_name_ar', 'gender', 'date_of_birth', 
            'phone_number', 'secondary_phone', 'email', 'address_en', 'address_ar', 
            'city', 'state_province', 'postal_code', 'country', 'national_id', 
            'passport_number', 'blood_type', 'emergency_contact_name', 
            'emergency_contact_phone', 'emergency_contact_relationship', 'notes'
        ]
    
    def validate_national_id(self, value):
        """Validate national ID format and uniqueness"""
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("National ID must be exactly 10 digits")
        
        if Patient.objects.filter(national_id=value, is_deleted=False).exists():
            raise serializers.ValidationError("A patient with this National ID already exists")
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number uniqueness"""
        if Patient.objects.filter(phone_number=value, is_deleted=False).exists():
            raise serializers.ValidationError("A patient with this phone number already exists")
        return value

