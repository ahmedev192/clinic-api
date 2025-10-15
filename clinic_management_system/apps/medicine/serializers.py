from rest_framework import serializers
from .models import Category, Medicine


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    
    class Meta:
        model = Category
        fields = [
            'id', 'name_en', 'name_ar', 'description_en', 'description_ar',
            'is_active', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class MedicineSerializer(serializers.ModelSerializer):
    """Serializer for Medicine model"""
    category_name = serializers.CharField(source='category.name_en', read_only=True)
    category_name_ar = serializers.CharField(source='category.name_ar', read_only=True)
    current_stock = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Medicine
        fields = [
            'id', 'internal_code', 'name_en', 'name_ar',
            'generic_name_en', 'generic_name_ar', 'brand_name_en', 'brand_name_ar',
            'category', 'category_name', 'category_name_ar',
            'dosage_form', 'strength', 'unit', 'reorder_level',
            'is_active', 'is_archived', 'base_cost', 'base_selling_price',
            'notes_en', 'notes_ar', 'usage_instructions_en', 'usage_instructions_ar',
            'current_stock', 'is_low_stock',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'current_stock', 'is_low_stock']

    def get_current_stock(self, obj):
        """Get current stock quantity"""
        return obj.get_current_stock()

    def get_is_low_stock(self, obj):
        """Check if medicine is low on stock"""
        return obj.is_low_stock()


class MedicineListSerializer(serializers.ModelSerializer):
    """Simplified serializer for medicine list views"""
    category_name = serializers.CharField(source='category.name_en', read_only=True)
    current_stock = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Medicine
        fields = [
            'id', 'internal_code', 'name_en', 'name_ar',
            'generic_name_en', 'brand_name_en', 'category_name',
            'dosage_form', 'strength', 'unit', 'reorder_level',
            'is_active', 'is_archived', 'current_stock', 'is_low_stock'
        ]

    def get_current_stock(self, obj):
        """Get current stock quantity"""
        return obj.get_current_stock()

    def get_is_low_stock(self, obj):
        """Check if medicine is low on stock"""
        return obj.is_low_stock()


class MedicineSearchSerializer(serializers.ModelSerializer):
    """Serializer for medicine search functionality"""
    
    class Meta:
        model = Medicine
        fields = [
            'id', 'internal_code', 'name_en', 'name_ar',
            'generic_name_en', 'generic_name_ar', 'brand_name_en', 'brand_name_ar',
            'dosage_form', 'strength', 'unit', 'is_active'
        ]
