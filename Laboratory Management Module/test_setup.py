#!/usr/bin/env python
"""
Simple test script to verify the Laboratory Management Module setup
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laboratory_management.settings')
django.setup()

def test_imports():
    """Test that all modules can be imported"""
    try:
        from lab_tests.models import TestCategory, LabTest
        from lab_requests.models import LabRequest, LabRequestItem
        from lab_samples.models import Sample, SampleCollection
        from lab_results.models import LabResult, ResultAttachment
        from lab_reports.models import LabReport, ReportTemplate, ReportDelivery
        print("✅ All models imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_models():
    """Test that models can be created"""
    try:
        from lab_tests.models import TestCategory, LabTest
        from django.contrib.auth.models import User
        
        # Create a test user
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        
        # Create a test category
        category, created = TestCategory.objects.get_or_create(
            name_en='Test Category',
            defaults={
                'name_ar': 'فئة الاختبار',
                'description_en': 'Test category for testing',
                'description_ar': 'فئة اختبار للاختبار'
            }
        )
        
        # Create a test lab test
        test, created = LabTest.objects.get_or_create(
            code='TEST001',
            defaults={
                'name_en': 'Test Lab Test',
                'name_ar': 'اختبار مختبر تجريبي',
                'category': category,
                'price': 100.00,
                'description_en': 'A test lab test',
                'description_ar': 'اختبار مختبر تجريبي',
                'created_by': user
            }
        )
        
        print("✅ Models can be created successfully")
        return True
    except Exception as e:
        print(f"❌ Model creation error: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints are properly configured"""
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test that the API schema endpoint exists
        response = client.get('/api/schema/')
        if response.status_code == 200:
            print("✅ API schema endpoint working")
        else:
            print(f"❌ API schema endpoint returned status {response.status_code}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ API endpoint test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Laboratory Management Module Setup")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Model Creation Test", test_models),
        ("API Endpoints Test", test_api_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Laboratory Management Module is ready to use.")
        print("\n📚 Next steps:")
        print("1. Run migrations: python manage.py migrate")
        print("2. Create superuser: python manage.py createsuperuser")
        print("3. Load sample data: python manage.py load_sample_data")
        print("4. Start server: python manage.py runserver")
        print("5. Visit API docs: http://localhost:8000/api/docs/")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
