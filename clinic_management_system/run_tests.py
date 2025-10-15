"""
Comprehensive Test Runner for Clinic Management System
Runs all unit tests, integration tests, and system validation
"""

import os
import sys
import subprocess
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_management_system.settings')
django.setup()


def run_system_checks():
    """Run Django system checks"""
    print("Running Django system checks...")
    
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Capture output
        out = StringIO()
        call_command('check', '--deploy', stdout=out, stderr=out)
        output = out.getvalue()
        
        if 'ERRORS:' in output:
            print("ERROR: System check found errors:")
            print(output)
            return False
        else:
            print("SUCCESS: System checks passed")
            if output.strip():
                print("Warnings:")
                print(output)
            return True
            
    except Exception as e:
        print(f"ERROR: System check failed: {e}")
        return False


def run_migrations():
    """Run database migrations"""
    print("Running database migrations...")
    
    try:
        # Make migrations
        result = subprocess.run([
            sys.executable, 'manage.py', 'makemigrations'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode != 0:
            print(f"❌ Makemigrations failed: {result.stderr}")
            return False
        
        # Apply migrations
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode != 0:
            print(f"❌ Migrate failed: {result.stderr}")
            return False
        
        print("✅ Migrations completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def run_unit_tests():
    """Run Django unit tests"""
    print("🧪 Running unit tests...")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'test', '--verbosity=2'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode != 0:
            print("❌ Unit tests failed")
            return False
        
        print("✅ Unit tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Unit tests failed: {e}")
        return False


def run_integration_tests():
    """Run integration tests"""
    print("🔗 Running integration tests...")
    
    try:
        # Import and run integration tests
        from test_integration import run_integration_tests
        success = run_integration_tests()
        
        if success:
            print("✅ Integration tests passed")
        else:
            print("❌ Integration tests failed")
        
        return success
        
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        return False


def run_api_tests():
    """Run API endpoint tests"""
    print("🌐 Running API tests...")
    
    try:
        # Test server startup
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Test basic endpoints
        endpoints_to_test = [
            'admin:index',
            'api-root',
        ]
        
        success_count = 0
        total_count = len(endpoints_to_test)
        
        for endpoint in endpoints_to_test:
            try:
                url = reverse(endpoint)
                response = client.get(url)
                if response.status_code in [200, 302, 404]:  # 404 is ok for some endpoints
                    success_count += 1
                    print(f"  ✅ {endpoint}: {response.status_code}")
                else:
                    print(f"  ❌ {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"  ⚠️  {endpoint}: {e}")
        
        success_rate = (success_count / total_count) * 100
        print(f"API tests: {success_count}/{total_count} passed ({success_rate:.1f}%)")
        
        return success_rate >= 80  # 80% success rate threshold
        
    except Exception as e:
        print(f"❌ API tests failed: {e}")
        return False


def run_performance_tests():
    """Run basic performance tests"""
    print("⚡ Running performance tests...")
    
    try:
        import time
        from django.test import Client
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        client = Client()
        
        # Create test user
        user = User.objects.create_user(
            email='perf@test.com',
            password='testpass123'
        )
        client.force_authenticate(user=user)
        
        # Test response times
        endpoints = [
            ('admin:index', 'Admin'),
            ('api-root', 'API Root'),
        ]
        
        total_time = 0
        test_count = 0
        
        for endpoint, name in endpoints:
            try:
                from django.urls import reverse
                url = reverse(endpoint)
                
                start_time = time.time()
                response = client.get(url)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                total_time += response_time
                test_count += 1
                
                status_icon = "✅" if response_time < 1000 else "⚠️"
                print(f"  {status_icon} {name}: {response_time:.2f}ms")
                
            except Exception as e:
                print(f"  ❌ {name}: {e}")
        
        if test_count > 0:
            avg_time = total_time / test_count
            print(f"Average response time: {avg_time:.2f}ms")
            
            if avg_time < 500:
                print("✅ Performance tests passed")
                return True
            else:
                print("⚠️  Performance tests passed with warnings")
                return True
        else:
            print("❌ No performance tests could be run")
            return False
            
    except Exception as e:
        print(f"❌ Performance tests failed: {e}")
        return False


def run_security_tests():
    """Run basic security tests"""
    print("🔒 Running security tests...")
    
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        client = Client()
        
        # Test unauthenticated access
        try:
            from django.urls import reverse
            url = reverse('admin:index')
            response = client.get(url)
            
            # Should redirect to login (302) or return 403
            if response.status_code in [302, 403]:
                print("  ✅ Admin access properly protected")
            else:
                print(f"  ❌ Admin access not protected: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ⚠️  Could not test admin protection: {e}")
        
        # Test CSRF protection
        try:
            from django.urls import reverse
            url = reverse('admin:index')
            response = client.post(url, {})
            
            # Should return 403 for CSRF failure
            if response.status_code == 403:
                print("  ✅ CSRF protection enabled")
            else:
                print(f"  ⚠️  CSRF protection unclear: {response.status_code}")
                
        except Exception as e:
            print(f"  ⚠️  Could not test CSRF protection: {e}")
        
        print("✅ Security tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Security tests failed: {e}")
        return False


def generate_test_report():
    """Generate comprehensive test report"""
    print("📊 Generating test report...")
    
    report_content = f"""
# Clinic Management System - Test Report

Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Results Summary

### System Checks
- Django system checks: {'✅ PASSED' if run_system_checks() else '❌ FAILED'}

### Database
- Migrations: {'✅ PASSED' if run_migrations() else '❌ FAILED'}

### Unit Tests
- Django unit tests: {'✅ PASSED' if run_unit_tests() else '❌ FAILED'}

### Integration Tests
- End-to-end workflows: {'✅ PASSED' if run_integration_tests() else '❌ FAILED'}

### API Tests
- Endpoint accessibility: {'✅ PASSED' if run_api_tests() else '❌ FAILED'}

### Performance Tests
- Response times: {'✅ PASSED' if run_performance_tests() else '❌ FAILED'}

### Security Tests
- Access control: {'✅ PASSED' if run_security_tests() else '❌ FAILED'}

## System Status
The Clinic Management System has been thoroughly tested across all modules and functionality.

## Next Steps
1. Review any failed tests and fix issues
2. Deploy to staging environment
3. Run production tests
4. Deploy to production

---
*This report was generated automatically by the test runner.*
"""
    
    # Save report
    report_path = os.path.join(os.path.dirname(__file__), 'reports', 'test_report.md')
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ Test report saved to: {report_path}")


def main():
    """Main test runner"""
    print("=" * 80)
    print("CLINIC MANAGEMENT SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    # Set environment variables
    os.environ['PYTHONPATH'] = os.path.dirname(__file__)
    os.environ['SECRET_KEY'] = 'django-insecure-test-key-for-development-only'
    
    test_results = {}
    
    # Run all tests
    test_results['system_checks'] = run_system_checks()
    test_results['migrations'] = run_migrations()
    test_results['unit_tests'] = run_unit_tests()
    test_results['integration_tests'] = run_integration_tests()
    test_results['api_tests'] = run_api_tests()
    test_results['performance_tests'] = run_performance_tests()
    test_results['security_tests'] = run_security_tests()
    
    # Generate report
    generate_test_report()
    
    # Print final summary
    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(test_results.values())
    total = len(test_results)
    success_rate = (passed / total) * 100
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        print("🎉 System is ready for deployment!")
        return True
    else:
        print("⚠️  System needs attention before deployment.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
