# Integration Guide

## Overview

This guide explains how to integrate the Consultation & Clinical Notes Module with other components of your Clinic Management System.

## Integration Points

### 1. Patients Module Integration

#### Data Exchange
- **Patient ID Reference**: The consultation module uses `patient_id` to link consultations to patient records
- **Patient History**: Maintains a complete consultation history per patient

#### Required Integration
```python
# In your Patients Module
class Patient(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    # ... other patient fields

# The consultation module will reference this ID
consultation = Consultation.objects.create(
    patient_id=patient.id,  # Reference to your patient
    doctor_id=doctor.id,
    # ... other fields
)
```

#### API Integration
```python
# Get patient consultations
GET /api/consultations/?patient_id=123

# Get consultation statistics for a patient
GET /api/consultations/statistics/?patient_id=123
```

### 2. Doctors Module Integration

#### Data Exchange
- **Doctor ID Reference**: The consultation module uses `doctor_id` to link consultations to doctor profiles
- **Specialization Support**: Supports filtering by doctor specialization

#### Required Integration
```python
# In your Doctors Module
class Doctor(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    specialization = models.CharField(max_length=100)
    # ... other doctor fields

# The consultation module will reference this ID
consultation = Consultation.objects.create(
    patient_id=patient.id,
    doctor_id=doctor.id,  # Reference to your doctor
    # ... other fields
)
```

#### API Integration
```python
# Get doctor consultations
GET /api/consultations/?doctor_id=456

# Get consultations by specialization (custom filter)
GET /api/consultations/?specialization=cardiology
```

### 3. Appointments Module Integration

#### Data Exchange
- **Appointment ID Reference**: Links consultations to scheduled appointments
- **Follow-up Linking**: Supports linking follow-up notes to future appointments

#### Required Integration
```python
# In your Appointments Module
class Appointment(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    patient_id = models.PositiveIntegerField()
    doctor_id = models.PositiveIntegerField()
    appointment_date = models.DateTimeField()
    # ... other appointment fields

# The consultation module will reference this ID
consultation = Consultation.objects.create(
    patient_id=appointment.patient_id,
    doctor_id=appointment.doctor_id,
    appointment_id=appointment.id,  # Reference to your appointment
    # ... other fields
)
```

#### API Integration
```python
# Get consultations for an appointment
GET /api/consultations/?appointment_id=789

# Link follow-up note to future appointment
POST /api/follow-up-notes/
{
    "consultation": "consultation-uuid",
    "linked_appointment_id": 123,
    "content_en": "Follow-up required",
    "content_ar": "متابعة مطلوبة"
}
```

### 4. Pharmacy Module Integration

#### Data Exchange
- **Prescription Status**: Tracks prescription fulfillment status
- **Medication Data**: Provides complete prescription details for dispensing

#### Integration Points
```python
# Prescription status updates
prescription = Prescription.objects.get(id=prescription_id)
prescription.pharmacy_status = 'dispensed'
prescription.pharmacy_notes = 'Prescription fulfilled'
prescription.save()

# Get prescriptions for pharmacy
GET /api/prescriptions/?pharmacy_status=pending
```

#### Webhook Integration (Optional)
```python
# Send prescription to pharmacy module
POST /api/prescriptions/{id}/send_to_pharmacy/
{
    "pharmacy_notes": "Urgent prescription"
}

# The system will update pharmacy_status to 'sent'
# You can implement webhooks to notify your pharmacy module
```

### 5. Laboratory Module Integration

#### Data Exchange
- **Lab Order Status**: Tracks test ordering and completion
- **Result Integration**: Supports lab result attachment and review

#### Integration Points
```python
# Lab order status updates
lab_order = LabOrder.objects.get(id=lab_order_id)
lab_order.lab_status = 'completed'
lab_order.lab_reference = 'LAB-REF-12345'
lab_order.save()

# Get lab orders for laboratory
GET /api/lab-orders/?lab_status=pending
```

#### Result Integration
```python
# Add lab results
POST /api/lab-orders/{id}/add_result/
{
    "result_value": "4.5",
    "reference_range": "4.0-5.5",
    "unit": "million/μL",
    "status": "normal",
    "interpretation_en": "Within normal range",
    "interpretation_ar": "ضمن المعدل الطبيعي"
}
```

## API Integration Patterns

### 1. RESTful API Integration

#### Authentication
```python
import requests

# Get authentication token
auth_response = requests.post('http://localhost:8000/api/auth/token/', {
    'username': 'your-username',
    'password': 'your-password'
})
token = auth_response.json()['token']

# Use token in subsequent requests
headers = {
    'Authorization': f'Token {token}',
    'Content-Type': 'application/json'
}
```

#### Creating Consultations
```python
# Create consultation from appointment
consultation_data = {
    'patient_id': appointment.patient_id,
    'doctor_id': appointment.doctor_id,
    'appointment_id': appointment.id,
    'consultation_type': 'new',
    'chief_complaint_en': 'Routine check-up',
    'chief_complaint_ar': 'فحص روتيني'
}

response = requests.post(
    'http://localhost:8000/api/consultations/',
    json=consultation_data,
    headers=headers
)
consultation = response.json()
```

#### Adding Diagnoses
```python
# Add diagnosis to consultation
diagnosis_data = {
    'diagnosis_id': 'diagnosis-uuid',
    'status': 'primary',
    'notes_en': 'Confirmed diagnosis',
    'notes_ar': 'تشخيص مؤكد'
}

response = requests.post(
    f'http://localhost:8000/api/consultations/{consultation_id}/add_diagnosis/',
    json=diagnosis_data,
    headers=headers
)
```

### 2. Webhook Integration

#### Setting up Webhooks
```python
# In your main Django project
from django.dispatch import Signal

# Define signals for integration
consultation_created = Signal()
prescription_sent = Signal()
lab_order_sent = Signal()

# In your consultation module
from django.dispatch import receiver

@receiver(consultation_created)
def notify_appointments_module(sender, consultation, **kwargs):
    # Notify appointments module about consultation completion
    pass

@receiver(prescription_sent)
def notify_pharmacy_module(sender, prescription, **kwargs):
    # Notify pharmacy module about new prescription
    pass
```

### 3. Database Integration

#### Direct Database Access
```python
# Access consultation data directly
from consultation.models import Consultation, Prescription, LabOrder

# Get patient consultations
patient_consultations = Consultation.objects.filter(patient_id=123)

# Get pending prescriptions
pending_prescriptions = Prescription.objects.filter(
    pharmacy_status='pending'
)

# Get lab orders for specific date range
lab_orders = LabOrder.objects.filter(
    ordered_date__range=[start_date, end_date]
)
```

## Data Synchronization

### 1. Real-time Updates

#### Using Django Signals
```python
# In your integration module
from django.db.models.signals import post_save
from django.dispatch import receiver
from consultation.models import Consultation

@receiver(post_save, sender=Consultation)
def update_patient_consultation_count(sender, instance, created, **kwargs):
    # Update patient consultation count
    if created:
        # Increment consultation count in patient record
        pass
```

### 2. Batch Processing

#### Scheduled Data Sync
```python
# Create management command for data synchronization
from django.core.management.base import BaseCommand
from consultation.models import Consultation

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Sync consultation data with other modules
        consultations = Consultation.objects.filter(
            status='completed',
            synced=False
        )
        
        for consultation in consultations:
            # Sync with other modules
            self.sync_with_patients_module(consultation)
            self.sync_with_pharmacy_module(consultation)
            consultation.synced = True
            consultation.save()
```

## Error Handling

### 1. API Error Handling
```python
import requests
from requests.exceptions import RequestException

try:
    response = requests.post(
        'http://localhost:8000/api/consultations/',
        json=consultation_data,
        headers=headers
    )
    response.raise_for_status()
    consultation = response.json()
except RequestException as e:
    # Handle API errors
    print(f"API Error: {e}")
except ValueError as e:
    # Handle JSON parsing errors
    print(f"JSON Error: {e}")
```

### 2. Data Validation
```python
# Validate data before integration
def validate_consultation_data(data):
    required_fields = ['patient_id', 'doctor_id', 'consultation_type']
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate patient and doctor exist
    if not Patient.objects.filter(id=data['patient_id']).exists():
        raise ValueError("Patient not found")
    
    if not Doctor.objects.filter(id=data['doctor_id']).exists():
        raise ValueError("Doctor not found")
```

## Performance Considerations

### 1. Database Optimization
```python
# Use select_related and prefetch_related for efficient queries
consultations = Consultation.objects.select_related(
    'created_by', 'updated_by'
).prefetch_related(
    'diagnoses__diagnosis',
    'prescriptions__items',
    'lab_orders__results'
)
```

### 2. Caching
```python
from django.core.cache import cache

# Cache frequently accessed data
def get_patient_consultations(patient_id):
    cache_key = f"patient_consultations_{patient_id}"
    consultations = cache.get(cache_key)
    
    if consultations is None:
        consultations = Consultation.objects.filter(patient_id=patient_id)
        cache.set(cache_key, consultations, 300)  # Cache for 5 minutes
    
    return consultations
```

### 3. Pagination
```python
# Use pagination for large datasets
from rest_framework.pagination import PageNumberPagination

class ConsultationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
```

## Security Considerations

### 1. Authentication
```python
# Use proper authentication for API access
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class ConsultationViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
```

### 2. Data Validation
```python
# Validate all input data
from rest_framework import serializers

class ConsultationSerializer(serializers.ModelSerializer):
    def validate_patient_id(self, value):
        if not Patient.objects.filter(id=value).exists():
            raise serializers.ValidationError("Patient not found")
        return value
```

### 3. Audit Logging
```python
# Log all integration activities
from consultation.models import AuditLog

def log_integration_activity(user, action, model_name, object_id):
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        ip_address=get_client_ip(),
        user_agent=get_user_agent()
    )
```

## Testing Integration

### 1. Unit Tests
```python
from django.test import TestCase
from consultation.models import Consultation

class ConsultationIntegrationTest(TestCase):
    def test_create_consultation_with_patient(self):
        # Test consultation creation with patient reference
        consultation = Consultation.objects.create(
            patient_id=123,
            doctor_id=456,
            consultation_type='new'
        )
        self.assertEqual(consultation.patient_id, 123)
```

### 2. Integration Tests
```python
import requests
from django.test import TestCase

class APIIntegrationTest(TestCase):
    def test_consultation_api_integration(self):
        # Test API integration
        response = requests.post(
            'http://localhost:8000/api/consultations/',
            json=consultation_data,
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
```

## Monitoring and Logging

### 1. Application Logging
```python
import logging

logger = logging.getLogger('consultation.integration')

def create_consultation_integration(consultation_data):
    try:
        # Create consultation
        consultation = Consultation.objects.create(**consultation_data)
        logger.info(f"Consultation created: {consultation.id}")
        return consultation
    except Exception as e:
        logger.error(f"Failed to create consultation: {e}")
        raise
```

### 2. Performance Monitoring
```python
import time
from django.db import connection

def monitor_query_performance():
    start_time = time.time()
    # Execute query
    consultations = Consultation.objects.filter(patient_id=123)
    end_time = time.time()
    
    query_time = end_time - start_time
    if query_time > 1.0:  # Log slow queries
        logger.warning(f"Slow query detected: {query_time}s")
```

This integration guide provides comprehensive information for integrating the Consultation & Clinical Notes Module with other components of your Clinic Management System. Follow these patterns and best practices to ensure smooth integration and optimal performance.
