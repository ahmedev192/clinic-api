"""
Django REST Framework serializers for the Consultation & Clinical Notes Module.
Supports multilingual data and comprehensive API responses.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Consultation, Diagnosis, ConsultationDiagnosis, Prescription, PrescriptionItem,
    LabOrder, LabResult, Attachment, FollowUpNote, AuditLog
)


class MultilingualSerializerMixin:
    """Mixin to provide multilingual field handling."""
    
    def to_representation(self, instance):
        """Add language-specific fields to representation."""
        data = super().to_representation(instance)
        
        # Add language-specific methods if they exist
        if hasattr(instance, 'get_chief_complaint'):
            data['chief_complaint'] = {
                'en': instance.get_chief_complaint('en'),
                'ar': instance.get_chief_complaint('ar')
            }
        
        if hasattr(instance, 'get_symptoms'):
            data['symptoms'] = {
                'en': instance.get_symptoms('en'),
                'ar': instance.get_symptoms('ar')
            }
        
        if hasattr(instance, 'get_name'):
            data['name'] = {
                'en': instance.get_name('en'),
                'ar': instance.get_name('ar')
            }
        
        if hasattr(instance, 'get_medication_name'):
            data['medication_name'] = {
                'en': instance.get_medication_name('en'),
                'ar': instance.get_medication_name('ar')
            }
        
        if hasattr(instance, 'get_instructions'):
            data['instructions'] = {
                'en': instance.get_instructions('en'),
                'ar': instance.get_instructions('ar')
            }
        
        if hasattr(instance, 'get_title'):
            data['title'] = {
                'en': instance.get_title('en'),
                'ar': instance.get_title('ar')
            }
        
        if hasattr(instance, 'get_content'):
            data['content'] = {
                'en': instance.get_content('en'),
                'ar': instance.get_content('ar')
            }
        
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (for API responses)."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class DiagnosisSerializer(MultilingualSerializerMixin, serializers.ModelSerializer):
    """Serializer for Diagnosis model."""
    
    class Meta:
        model = Diagnosis
        fields = [
            'id', 'diagnosis_code', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'category', 'is_chronic', 'is_contagious', 'severity_level', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class ConsultationDiagnosisSerializer(MultilingualSerializerMixin, serializers.ModelSerializer):
    """Serializer for ConsultationDiagnosis model."""
    
    diagnosis = DiagnosisSerializer(read_only=True)
    diagnosis_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = ConsultationDiagnosis
        fields = [
            'id', 'diagnosis', 'diagnosis_id', 'status', 'notes_en', 'notes_ar',
            'onset_date', 'is_resolved', 'resolution_date', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class PrescriptionItemSerializer(MultilingualSerializerMixin, serializers.ModelSerializer):
    """Serializer for PrescriptionItem model."""
    
    class Meta:
        model = PrescriptionItem
        fields = [
            'id', 'medication_name_en', 'medication_name_ar', 'generic_name_en', 'generic_name_ar',
            'dosage', 'frequency', 'custom_frequency', 'duration_days', 'quantity',
            'instructions_en', 'instructions_ar', 'is_controlled_substance', 'requires_refrigerator',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class PrescriptionSerializer(MultilingualSerializerMixin, serializers.ModelSerializer):
    """Serializer for Prescription model."""
    
    items = PrescriptionItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'prescription_code', 'consultation', 'status', 'notes_en', 'notes_ar',
            'prescribed_date', 'valid_until', 'pharmacy_status', 'pharmacy_notes',
            'items', 'created', 'modified'
        ]
        read_only_fields = ['id', 'prescription_code', 'created', 'modified']


class LabResultSerializer(MultilingualSerializerMixin, serializers.ModelSerializer):
    """Serializer for LabResult model."""
    
    reviewed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = LabResult
        fields = [
            'id', 'lab_order', 'result_value', 'reference_range', 'unit', 'status',
            'interpretation_en', 'interpretation_ar', 'result_date', 'reviewed_by',
            'reviewed_date', 'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class LabOrderSerializer(MultilingualSerializerMixin, serializers.ModelSerializer):
    """Serializer for LabOrder model."""
    
    results = LabResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = LabOrder
        fields = [
            'id', 'order_code', 'consultation', 'test_name_en', 'test_name_ar',
            'test_category', 'priority', 'status', 'clinical_justification_en',
            'clinical_justification_ar', 'ordered_date', 'requested_date',
            'lab_reference', 'lab_status', 'results', 'created', 'modified'
        ]
        read_only_fields = ['id', 'order_code', 'created', 'modified']


class AttachmentSerializer(MultilingualSerializerMixin, serializers.ModelSerializer):
    """Serializer for Attachment model."""
    
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Attachment
        fields = [
            'id', 'consultation', 'file', 'file_url', 'file_name', 'file_type',
            'file_size', 'title_en', 'title_ar', 'description_en', 'description_ar',
            'is_confidential', 'access_level', 'uploaded_by', 'created', 'modified'
        ]
        read_only_fields = ['id', 'file_size', 'created', 'modified']
    
    def get_file_url(self, obj):
        """Get the file URL."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class FollowUpNoteSerializer(MultilingualSerializerMixin, serializers.ModelSerializer):
    """Serializer for FollowUpNote model."""
    
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = FollowUpNote
        fields = [
            'id', 'consultation', 'note_type', 'content_en', 'content_ar',
            'note_date', 'is_urgent', 'linked_appointment_id', 'created_by',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'created', 'modified']


class ConsultationSerializer(MultilingualSerializerMixin, serializers.ModelSerializer):
    """Serializer for Consultation model."""
    
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    diagnoses = ConsultationDiagnosisSerializer(many=True, read_only=True)
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    lab_orders = LabOrderSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    follow_up_notes = FollowUpNoteSerializer(many=True, read_only=True)
    
    # Patient and Doctor information (for display)
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultation
        fields = [
            'id', 'consultation_code', 'patient_id', 'doctor_id', 'appointment_id',
            'consultation_type', 'status', 'chief_complaint_en', 'chief_complaint_ar',
            'symptoms_en', 'symptoms_ar', 'examination_findings_en', 'examination_findings_ar',
            'assessment_notes_en', 'assessment_notes_ar', 'consultation_date', 'duration_minutes',
            'created_by', 'updated_by', 'patient_name', 'doctor_name',
            'diagnoses', 'prescriptions', 'lab_orders', 'attachments', 'follow_up_notes',
            'created', 'modified'
        ]
        read_only_fields = ['id', 'consultation_code', 'created', 'modified']
    
    def get_patient_name(self, obj):
        """Get patient name (placeholder for integration)."""
        # This would integrate with the Patients Module
        return f"Patient {obj.patient_id}"
    
    def get_doctor_name(self, obj):
        """Get doctor name (placeholder for integration)."""
        # This would integrate with the Doctors Module
        return f"Doctor {obj.doctor_id}"


class ConsultationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating consultations."""
    
    class Meta:
        model = Consultation
        fields = [
            'patient_id', 'doctor_id', 'appointment_id', 'consultation_type',
            'chief_complaint_en', 'chief_complaint_ar', 'symptoms_en', 'symptoms_ar',
            'examination_findings_en', 'examination_findings_ar', 'assessment_notes_en',
            'assessment_notes_ar', 'consultation_date', 'duration_minutes'
        ]
    
    def create(self, validated_data):
        """Create consultation with auto-generated code."""
        # Generate consultation code
        import uuid
        consultation_code = f"CONS-{uuid.uuid4().hex[:8].upper()}"
        validated_data['consultation_code'] = consultation_code
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating prescriptions."""
    items = PrescriptionItemSerializer(many=True)
    
    class Meta:
        model = Prescription
        fields = [
            'consultation', 'notes_en', 'notes_ar', 'valid_until', 'items'
        ]
    
    def create(self, validated_data):
        """Create prescription with items."""
        items_data = validated_data.pop('items')
        
        # Generate prescription code
        import uuid
        prescription_code = f"RX-{uuid.uuid4().hex[:8].upper()}"
        validated_data['prescription_code'] = prescription_code
        
        prescription = Prescription.objects.create(**validated_data)
        
        # Create prescription items
        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)
        
        return prescription


class LabOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating lab orders."""
    
    class Meta:
        model = LabOrder
        fields = [
            'consultation', 'test_name_en', 'test_name_ar', 'test_category',
            'priority', 'clinical_justification_en', 'clinical_justification_ar',
            'requested_date'
        ]
    
    def create(self, validated_data):
        """Create lab order with auto-generated code."""
        import uuid
        order_code = f"LAB-{uuid.uuid4().hex[:8].upper()}"
        validated_data['order_code'] = order_code
        return super().create(validated_data)


class ConsultationSearchSerializer(serializers.Serializer):
    """Serializer for consultation search parameters."""
    
    patient_id = serializers.IntegerField(required=False)
    doctor_id = serializers.IntegerField(required=False)
    consultation_type = serializers.ChoiceField(
        choices=Consultation.CONSULTATION_TYPES,
        required=False
    )
    status = serializers.ChoiceField(
        choices=Consultation.STATUS_CHOICES,
        required=False
    )
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    search_text = serializers.CharField(required=False)
    
    def validate(self, data):
        """Validate search parameters."""
        if 'date_from' in data and 'date_to' in data:
            if data['date_from'] > data['date_to']:
                raise serializers.ValidationError(
                    "date_from must be before date_to"
                )
        return data


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'action', 'model_name', 'object_id',
            'old_values', 'new_values', 'ip_address', 'user_agent',
            'created'
        ]
        read_only_fields = ['id', 'created']


class ConsultationStatsSerializer(serializers.Serializer):
    """Serializer for consultation statistics."""
    
    total_consultations = serializers.IntegerField()
    completed_consultations = serializers.IntegerField()
    draft_consultations = serializers.IntegerField()
    consultations_by_type = serializers.DictField()
    consultations_by_status = serializers.DictField()
    average_duration = serializers.FloatField()
    total_prescriptions = serializers.IntegerField()
    total_lab_orders = serializers.IntegerField()
    total_attachments = serializers.IntegerField()
