"""
Serializers for Staff Management API
Supports bilingual operation (Arabic + English)
"""

from rest_framework import serializers
from apps.accounts.models import User
from .models import (
    Role, Specialization, Staff, Doctor, Schedule, 
    Compensation, StaffAuditLog
)


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model"""
    
    class Meta:
        model = Role
        fields = [
            'id', 'code', 'name_en', 'name_ar', 'description_en', 
            'description_ar', 'is_active', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class SpecializationSerializer(serializers.ModelSerializer):
    """Serializer for Specialization model"""
    
    class Meta:
        model = Specialization
        fields = [
            'id', 'name_en', 'name_ar', 'description_en', 
            'description_ar', 'is_active', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (simplified)"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']
        read_only_fields = ['id']


class StaffListSerializer(serializers.ModelSerializer):
    """Simplified serializer for staff list views"""
    role = RoleSerializer(read_only=True)
    full_name_en = serializers.ReadOnlyField()
    full_name_ar = serializers.ReadOnlyField()
    
    class Meta:
        model = Staff
        fields = [
            'id', 'staff_id', 'full_name_en', 'full_name_ar', 'role',
            'employment_status', 'email', 'phone_primary', 'joining_date',
            'profile_image', 'is_removed'
        ]
        read_only_fields = ['id', 'staff_id', 'full_name_en', 'full_name_ar']


class StaffSerializer(serializers.ModelSerializer):
    """Full serializer for Staff model"""
    user = UserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True)
    full_name_en = serializers.ReadOnlyField()
    full_name_ar = serializers.ReadOnlyField()
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Staff
        fields = [
            'id', 'staff_id', 'user', 'role', 'role_id',
            'first_name_en', 'first_name_ar', 'last_name_en', 'last_name_ar',
            'middle_name_en', 'middle_name_ar', 'full_name_en', 'full_name_ar',
            'email', 'phone_primary', 'phone_secondary',
            'address_en', 'address_ar', 'city', 'country',
            'gender', 'date_of_birth', 'national_id', 'passport_number',
            'employment_status', 'joining_date', 'termination_date',
            'profile_image', 'profile_image_url', 'created', 'modified'
        ]
        read_only_fields = ['id', 'staff_id', 'user', 'created', 'modified']
    
    def get_profile_image_url(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
        return None


class StaffCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new staff members"""
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    role_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Staff
        fields = [
            'username', 'password', 'role_id',
            'first_name_en', 'first_name_ar', 'last_name_en', 'last_name_ar',
            'middle_name_en', 'middle_name_ar',
            'email', 'phone_primary', 'phone_secondary',
            'address_en', 'address_ar', 'city', 'country',
            'gender', 'date_of_birth', 'national_id', 'passport_number',
            'employment_status', 'joining_date', 'profile_image'
        ]
    
    def create(self, validated_data):
        # Create user account
        user_data = {
            'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'email': validated_data.get('email'),
            'first_name': validated_data.get('first_name_en', ''),
            'last_name': validated_data.get('last_name_en', ''),
        }
        
        user = User.objects.create_user(**user_data)
        
        # Create staff profile
        role_id = validated_data.pop('role_id')
        staff = Staff.objects.create(
            user=user,
            role_id=role_id,
            created_by=self.context['request'].user,
            **validated_data
        )
        
        return staff


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for Doctor model"""
    staff = StaffSerializer(read_only=True)
    staff_id = serializers.IntegerField(write_only=True)
    specializations = SpecializationSerializer(many=True, read_only=True)
    specialization_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    specializations_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'staff', 'staff_id', 'medical_license_number',
            'professional_title_en', 'professional_title_ar',
            'specializations', 'specialization_ids', 'specializations_display',
            'years_of_experience', 'biography_en', 'biography_ar',
            'languages', 'consultation_fee', 'hourly_rate',
            'is_available', 'is_accepting_new_patients', 'created', 'modified'
        ]
        read_only_fields = ['id', 'staff', 'created', 'modified']
    
    def create(self, validated_data):
        specialization_ids = validated_data.pop('specialization_ids', [])
        doctor = Doctor.objects.create(**validated_data)
        doctor.specializations.set(specialization_ids)
        return doctor
    
    def update(self, instance, validated_data):
        specialization_ids = validated_data.pop('specialization_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if specialization_ids is not None:
            instance.specializations.set(specialization_ids)
        
        return instance


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Schedule model"""
    staff = StaffListSerializer(read_only=True)
    staff_id = serializers.IntegerField(write_only=True)
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'staff', 'staff_id', 'day_of_week', 'day_of_week_display',
            'start_time', 'end_time', 'is_active', 'notes', 'created', 'modified'
        ]
        read_only_fields = ['id', 'staff', 'created', 'modified']


class CompensationSerializer(serializers.ModelSerializer):
    """Serializer for Compensation model"""
    staff = StaffListSerializer(read_only=True)
    staff_id = serializers.IntegerField(write_only=True)
    compensation_type_display = serializers.CharField(
        source='get_compensation_type_display', 
        read_only=True
    )
    
    class Meta:
        model = Compensation
        fields = [
            'id', 'staff', 'staff_id', 'compensation_type', 'compensation_type_display',
            'base_salary', 'commission_percentage', 'commission_per_appointment',
            'effective_from', 'effective_until', 'notes', 'created', 'modified'
        ]
        read_only_fields = ['id', 'staff', 'created', 'modified']


class StaffAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for StaffAuditLog model"""
    staff = StaffListSerializer(read_only=True)
    changed_by = UserSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = StaffAuditLog
        fields = [
            'id', 'staff', 'action', 'action_display', 'field_name',
            'old_value', 'new_value', 'changed_by', 'notes', 'created'
        ]
        read_only_fields = ['id', 'created']


class StaffSearchSerializer(serializers.Serializer):
    """Serializer for staff search functionality"""
    query = serializers.CharField(required=False, allow_blank=True)
    role = serializers.CharField(required=False, allow_blank=True)
    employment_status = serializers.CharField(required=False, allow_blank=True)
    specialization = serializers.CharField(required=False, allow_blank=True)
    is_available = serializers.BooleanField(required=False)
    language = serializers.CharField(required=False, default='en')
    
    def validate_language(self, value):
        if value not in ['en', 'ar']:
            raise serializers.ValidationError("Language must be 'en' or 'ar'")
        return value


class StaffStatsSerializer(serializers.Serializer):
    """Serializer for staff statistics"""
    total_staff = serializers.IntegerField()
    active_staff = serializers.IntegerField()
    doctors = serializers.IntegerField()
    nurses = serializers.IntegerField()
    receptionists = serializers.IntegerField()
    by_role = serializers.DictField()
    by_status = serializers.DictField()
    by_specialization = serializers.DictField()

