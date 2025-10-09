"""
Simple API test script for Staff Management Module
Run this after setting up the system to test the API endpoints
"""

import requests
import json
from datetime import date, time


class StaffAPITester:
    """Simple API tester for staff management endpoints"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def login(self, username="admin", password="admin123"):
        """Login and get authentication token"""
        url = f"{self.base_url}/api/auth/login/"
        data = {"username": username, "password": password}
        
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                self.token = response.json().get('token')
                self.session.headers.update({'Authorization': f'Token {self.token}'})
                print(f"✓ Logged in as {username}")
                return True
            else:
                print(f"✗ Login failed: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            print("✗ Connection failed. Make sure the server is running.")
            return False
    
    def test_roles(self):
        """Test roles endpoint"""
        print("\n--- Testing Roles ---")
        url = f"{self.base_url}/api/roles/"
        response = self.session.get(url)
        
        if response.status_code == 200:
            roles = response.json()
            print(f"✓ Found {len(roles['results'])} roles")
            for role in roles['results'][:3]:  # Show first 3
                print(f"  - {role['name_en']} ({role['code']})")
        else:
            print(f"✗ Roles request failed: {response.status_code}")
    
    def test_staff(self):
        """Test staff endpoint"""
        print("\n--- Testing Staff ---")
        url = f"{self.base_url}/api/staff/"
        response = self.session.get(url)
        
        if response.status_code == 200:
            staff = response.json()
            print(f"✓ Found {len(staff['results'])} staff members")
            for member in staff['results'][:3]:  # Show first 3
                print(f"  - {member['full_name_en']} ({member['role']['name_en']})")
        else:
            print(f"✗ Staff request failed: {response.status_code}")
    
    def test_doctors(self):
        """Test doctors endpoint"""
        print("\n--- Testing Doctors ---")
        url = f"{self.base_url}/api/doctors/"
        response = self.session.get(url)
        
        if response.status_code == 200:
            doctors = response.json()
            print(f"✓ Found {len(doctors['results'])} doctors")
            for doctor in doctors['results']:
                print(f"  - {doctor['staff']['full_name_en']} - {doctor['specializations_display']}")
        else:
            print(f"✗ Doctors request failed: {response.status_code}")
    
    def test_schedules(self):
        """Test schedules endpoint"""
        print("\n--- Testing Schedules ---")
        url = f"{self.base_url}/api/schedules/"
        response = self.session.get(url)
        
        if response.status_code == 200:
            schedules = response.json()
            print(f"✓ Found {len(schedules['results'])} schedules")
        else:
            print(f"✗ Schedules request failed: {response.status_code}")
    
    def test_search(self):
        """Test search functionality"""
        print("\n--- Testing Search ---")
        url = f"{self.base_url}/api/staff/search/"
        response = self.session.get(url, params={'query': 'doctor'})
        
        if response.status_code == 200:
            results = response.json()
            print(f"✓ Search found {len(results)} results for 'doctor'")
        else:
            print(f"✗ Search request failed: {response.status_code}")
    
    def test_stats(self):
        """Test statistics endpoint"""
        print("\n--- Testing Statistics ---")
        url = f"{self.base_url}/api/staff/stats/"
        response = self.session.get(url)
        
        if response.status_code == 200:
            stats = response.json()
            print("✓ Staff Statistics:")
            print(f"  - Total Staff: {stats['total_staff']}")
            print(f"  - Active Staff: {stats['active_staff']}")
            print(f"  - Doctors: {stats['doctors']}")
            print(f"  - Nurses: {stats['nurses']}")
        else:
            print(f"✗ Stats request failed: {response.status_code}")
    
    def test_doctor_availability(self):
        """Test doctor availability check"""
        print("\n--- Testing Doctor Availability ---")
        
        # First get a doctor
        url = f"{self.base_url}/api/doctors/"
        response = self.session.get(url)
        
        if response.status_code == 200 and response.json()['results']:
            doctor = response.json()['results'][0]
            doctor_id = doctor['id']
            
            # Check availability
            url = f"{self.base_url}/api/doctors/{doctor_id}/availability/"
            response = self.session.get(url, params={
                'date': '2024-01-01',  # Monday
                'time': '10:00'
            })
            
            if response.status_code == 200:
                availability = response.json()
                print(f"✓ Doctor {availability['doctor']} availability:")
                print(f"  - Date: {availability['date']}")
                print(f"  - Time: {availability['time']}")
                print(f"  - Available: {availability['is_available']}")
            else:
                print(f"✗ Availability check failed: {response.status_code}")
        else:
            print("✗ No doctors found for availability test")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Staff Management API Test Suite")
        print("=" * 40)
        
        if not self.login():
            return
        
        self.test_roles()
        self.test_staff()
        self.test_doctors()
        self.test_schedules()
        self.test_search()
        self.test_stats()
        self.test_doctor_availability()
        
        print("\n" + "=" * 40)
        print("✅ API testing completed!")


def main():
    """Main function"""
    tester = StaffAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
