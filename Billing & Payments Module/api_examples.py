"""
API Usage Examples for the Billing & Payments Module.

This file contains examples of how to use the API endpoints.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api"
USERNAME = "admin"
PASSWORD = "admin123"

# Get authentication token
def get_auth_token():
    """Get authentication token."""
    response = requests.post(f"{BASE_URL}/auth/token/", {
        'username': USERNAME,
        'password': PASSWORD
    })
    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"Authentication failed: {response.text}")
        return None

# Set up session with authentication
def setup_session():
    """Set up authenticated session."""
    token = get_auth_token()
    if not token:
        return None
    
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    })
    return session

# Example 1: Create a new patient
def create_patient(session):
    """Create a new patient."""
    patient_data = {
        "patient_id": "P004",
        "first_name_en": "Omar",
        "first_name_ar": "عمر",
        "last_name_en": "Al-Rashid",
        "last_name_ar": "الرشيد",
        "phone": "+966501234570",
        "email": "omar.alrashid@email.com",
        "date_of_birth": "1985-03-15"
    }
    
    response = session.post(f"{BASE_URL}/patients/", json=patient_data)
    if response.status_code == 201:
        print("Patient created successfully:")
        print(json.dumps(response.json(), indent=2))
        return response.json()['id']
    else:
        print(f"Failed to create patient: {response.text}")
        return None

# Example 2: Create a new invoice
def create_invoice(session, patient_id, doctor_id, service_id):
    """Create a new invoice."""
    invoice_data = {
        "patient": patient_id,
        "doctor": doctor_id,
        "visit_reference": "VISIT-001",
        "tax_rate": 15.0,
        "notes_en": "Regular consultation",
        "notes_ar": "استشارة عادية",
        "invoice_date": datetime.now().isoformat(),
        "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "items": [
            {
                "service": service_id,
                "description_en": "General consultation",
                "description_ar": "استشارة عامة",
                "quantity": 1,
                "unit_price": "150.00"
            }
        ]
    }
    
    response = session.post(f"{BASE_URL}/invoices/", json=invoice_data)
    if response.status_code == 201:
        print("Invoice created successfully:")
        print(json.dumps(response.json(), indent=2))
        return response.json()['id']
    else:
        print(f"Failed to create invoice: {response.text}")
        return None

# Example 3: Record a payment
def record_payment(session, invoice_id, payment_method_id):
    """Record a payment for an invoice."""
    payment_data = {
        "invoice": invoice_id,
        "payment_method": payment_method_id,
        "amount": "150.00",
        "reference_number": "PAY-001",
        "payment_date": datetime.now().isoformat(),
        "notes_en": "Cash payment",
        "notes_ar": "دفعة نقدية"
    }
    
    response = session.post(f"{BASE_URL}/payments/", json=payment_data)
    if response.status_code == 201:
        print("Payment recorded successfully:")
        print(json.dumps(response.json(), indent=2))
        return response.json()['id']
    else:
        print(f"Failed to record payment: {response.text}")
        return None

# Example 4: Get financial summary
def get_financial_summary(session):
    """Get financial summary."""
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    response = session.get(f"{BASE_URL}/reports/summary/?start_date={start_date}&end_date={end_date}")
    if response.status_code == 200:
        print("Financial Summary:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to get financial summary: {response.text}")

# Example 5: Search invoices
def search_invoices(session, patient_name=None, status=None):
    """Search invoices with filters."""
    params = {}
    if patient_name:
        params['search'] = patient_name
    if status:
        params['status'] = status
    
    response = session.get(f"{BASE_URL}/invoices/", params=params)
    if response.status_code == 200:
        print("Search Results:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to search invoices: {response.text}")

# Example 6: Apply discount to invoice
def apply_discount(session, discount_id, invoice_id):
    """Apply a discount to an invoice."""
    response = session.post(f"{BASE_URL}/discounts/{discount_id}/apply_to_invoice/", 
                          json={"invoice_id": invoice_id})
    if response.status_code == 200:
        print("Discount applied successfully:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to apply discount: {response.text}")

# Main execution
def main():
    """Run all examples."""
    print("Billing & Payments Module - API Examples")
    print("=" * 50)
    
    # Set up authenticated session
    session = setup_session()
    if not session:
        print("Failed to set up authentication. Please check credentials.")
        return
    
    print("1. Creating a new patient...")
    patient_id = create_patient(session)
    
    if patient_id:
        print("\n2. Getting available doctors and services...")
        # Get first doctor
        doctors_response = session.get(f"{BASE_URL}/doctors/")
        if doctors_response.status_code == 200:
            doctors = doctors_response.json()['results']
            if doctors:
                doctor_id = doctors[0]['id']
                print(f"Using doctor: {doctors[0]['full_name_en']}")
        
        # Get first service
        services_response = session.get(f"{BASE_URL}/services/")
        if services_response.status_code == 200:
            services = services_response.json()['results']
            if services:
                service_id = services[0]['id']
                print(f"Using service: {services[0]['name_en']}")
        
        print("\n3. Creating a new invoice...")
        invoice_id = create_invoice(session, patient_id, doctor_id, service_id)
        
        if invoice_id:
            print("\n4. Getting payment methods...")
            payment_methods_response = session.get(f"{BASE_URL}/payment-methods/")
            if payment_methods_response.status_code == 200:
                payment_methods = payment_methods_response.json()['results']
                if payment_methods:
                    payment_method_id = payment_methods[0]['id']
                    print(f"Using payment method: {payment_methods[0]['name_en']}")
            
            print("\n5. Recording a payment...")
            record_payment(session, invoice_id, payment_method_id)
    
    print("\n6. Getting financial summary...")
    get_financial_summary(session)
    
    print("\n7. Searching invoices...")
    search_invoices(session, patient_name="Omar")
    
    print("\nAPI Examples completed!")

if __name__ == "__main__":
    main()
