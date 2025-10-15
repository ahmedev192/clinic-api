from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import TestCategory, LabTest


class TestCategorySerializer(serializers.ModelSerializer):
    """Serializer for TestCategory model"""
    
    class Meta:
        model = TestCategory
        fields = [
            'id', 'name_en', 'name_ar', 'description_en', 'description_ar', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LabTestSerializer(serializers.ModelSerializer):
    """Serializer for LabTest model"""
    category_name_en = serializers.CharField(source='category.name_en', read_only=True)
    category_name_ar = serializers.CharField(source='category.name_ar', read_only=True)
    
    class Meta:
        model = LabTest
        fields = [
            'id', 'name_en', 'name_ar', 'category', 'category_name_en', 'category_name_ar',
            'code', 'price', 'normal_range_en', 'normal_range_ar', 'description_en', 
            'description_ar', 'preparation_instructions_en', 'preparation_instructions_ar',
            'unit', 'sample_type', 'processing_time_hours', 'is_active', 
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        """Set the created_by field to the current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class LabTestListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    category_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LabTest
        fields = [
            'id', 'name_en', 'name_ar', 'category', 'category_name', 'code', 
            'price', 'unit', 'sample_type', 'is_active'
        ]
    
    def get_category_name(self, obj):
        """Return category name based on current language"""
        from django.utils import translation
        if translation.get_language() == 'ar':
            return obj.category.name_ar
        return obj.category.name_en


class LabTestSearchSerializer(serializers.Serializer):
    """Serializer for test search functionality"""
    query = serializers.CharField(max_length=200, help_text=_("Search term for test name or code"))
    category = serializers.IntegerField(required=False, help_text=_("Filter by category ID"))
    is_active = serializers.BooleanField(required=False, help_text=_("Filter by active status"))
