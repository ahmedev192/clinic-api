from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lab_tests.models import TestCategory, LabTest


class Command(BaseCommand):
    help = 'Load sample data for testing'

    def handle(self, *args, **options):
        # Create superuser if doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create test categories
        categories_data = [
            {
                'name_en': 'Blood Tests',
                'name_ar': 'فحوصات الدم',
                'description_en': 'Various blood tests and hematology',
                'description_ar': 'فحوصات الدم المختلفة ودراسة الدم'
            },
            {
                'name_en': 'Urine Tests',
                'name_ar': 'فحوصات البول',
                'description_en': 'Urine analysis and related tests',
                'description_ar': 'تحليل البول والفحوصات ذات الصلة'
            },
            {
                'name_en': 'Biochemistry',
                'name_ar': 'الكيمياء الحيوية',
                'description_en': 'Biochemical tests and metabolic panels',
                'description_ar': 'الفحوصات الكيميائية الحيوية ولوحات التمثيل الغذائي'
            },
            {
                'name_en': 'Microbiology',
                'name_ar': 'علم الأحياء الدقيقة',
                'description_en': 'Microbiological tests and cultures',
                'description_ar': 'الفحوصات الميكروبيولوجية والمزارع'
            }
        ]

        for cat_data in categories_data:
            category, created = TestCategory.objects.get_or_create(
                name_en=cat_data['name_en'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name_en}')

        # Create sample lab tests
        tests_data = [
            {
                'name_en': 'Complete Blood Count (CBC)',
                'name_ar': 'تعداد الدم الكامل',
                'category_name': 'Blood Tests',
                'code': 'CBC001',
                'price': 50.00,
                'normal_range_en': 'WBC: 4.5-11.0 K/μL, RBC: 4.5-5.9 M/μL',
                'normal_range_ar': 'كريات الدم البيضاء: 4.5-11.0 ألف/ميكرولتر، كريات الدم الحمراء: 4.5-5.9 مليون/ميكرولتر',
                'description_en': 'Complete blood count including white blood cells, red blood cells, and platelets',
                'description_ar': 'تعداد الدم الكامل يشمل كريات الدم البيضاء والحمراء والصفائح الدموية',
                'preparation_instructions_en': 'No special preparation required',
                'preparation_instructions_ar': 'لا توجد تحضيرات خاصة مطلوبة',
                'unit': 'Various',
                'sample_type': 'blood',
                'processing_time_hours': 2
            },
            {
                'name_en': 'Blood Glucose (Fasting)',
                'name_ar': 'سكر الدم (صائم)',
                'category_name': 'Biochemistry',
                'code': 'GLU001',
                'price': 25.00,
                'normal_range_en': '70-100 mg/dL',
                'normal_range_ar': '70-100 مجم/ديسيلتر',
                'description_en': 'Fasting blood glucose level measurement',
                'description_ar': 'قياس مستوى السكر في الدم أثناء الصيام',
                'preparation_instructions_en': 'Fast for 8-12 hours before test',
                'preparation_instructions_ar': 'الصيام لمدة 8-12 ساعة قبل الفحص',
                'unit': 'mg/dL',
                'sample_type': 'blood',
                'processing_time_hours': 1
            },
            {
                'name_en': 'Urinalysis',
                'name_ar': 'تحليل البول',
                'category_name': 'Urine Tests',
                'code': 'UR001',
                'price': 30.00,
                'normal_range_en': 'Normal appearance, no protein, no glucose',
                'normal_range_ar': 'مظهر طبيعي، لا بروتين، لا سكر',
                'description_en': 'Complete urinalysis including physical, chemical, and microscopic examination',
                'description_ar': 'تحليل البول الكامل يشمل الفحص الفيزيائي والكيميائي والمجهري',
                'preparation_instructions_en': 'Clean catch midstream urine sample',
                'preparation_instructions_ar': 'عينة بول نظيفة من منتصف التيار',
                'unit': 'Various',
                'sample_type': 'urine',
                'processing_time_hours': 1
            },
            {
                'name_en': 'Cholesterol Total',
                'name_ar': 'الكوليسترول الكلي',
                'category_name': 'Biochemistry',
                'code': 'CHOL001',
                'price': 35.00,
                'normal_range_en': '< 200 mg/dL',
                'normal_range_ar': '< 200 مجم/ديسيلتر',
                'description_en': 'Total cholesterol level measurement',
                'description_ar': 'قياس مستوى الكوليسترول الكلي',
                'preparation_instructions_en': 'Fast for 12 hours before test',
                'preparation_instructions_ar': 'الصيام لمدة 12 ساعة قبل الفحص',
                'unit': 'mg/dL',
                'sample_type': 'blood',
                'processing_time_hours': 4
            }
        ]

        for test_data in tests_data:
            category = TestCategory.objects.get(name_en=test_data['category_name'])
            test_data['category'] = category
            del test_data['category_name']
            
            test, created = LabTest.objects.get_or_create(
                code=test_data['code'],
                defaults=test_data
            )
            if created:
                self.stdout.write(f'Created test: {test.name_en}')

        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
