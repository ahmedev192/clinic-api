# Patient Management Module - Clinic Management System

A comprehensive Django backend module for patient management in a clinic management system. This module provides full multilingual support (Arabic/English), audit logging, and is designed for easy integration with other system modules.

## Features

### Core Functionality
- **Patient Registration & Profile Management**
  - Complete patient information with multilingual support
  - Unique patient code generation
  - Duplicate prevention (phone number, national ID)
  - Soft delete functionality
  - Patient status management (active, inactive, archived)

- **Medical History Management**
  - Track diagnoses, surgeries, treatments, hospitalizations
  - Multilingual notes and descriptions
  - ICD-10 code support
  - Comprehensive audit logging

- **Allergies & Chronic Conditions**
  - Allergy tracking with severity levels
  - Chronic condition management
  - Medication tracking
  - Multilingual support for all text fields

- **Document Management**
  - Secure file upload and storage
  - Document type categorization
  - Verification system
  - Metadata tracking

### Advanced Features
- **Multilingual Support**
  - Arabic and English text fields
  - Automatic language detection
  - Multilingual search capabilities

- **Audit & Security**
  - Comprehensive audit logging
  - Patient access tracking
  - Data export logging
  - System event monitoring

- **Search & Filtering**
  - Advanced search across all fields
  - Multilingual search support
  - Complex filtering options
  - Search analytics

- **API & Integration**
  - RESTful API with DRF
  - Role-based permissions
  - Export functionality
  - Integration-ready design

## Installation

### Prerequisites
- Python 3.8+
- Django 4.2+
- PostgreSQL (recommended) or SQLite

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd clinic-management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Create sample data (optional)**
   ```bash
   python manage.py create_sample_data --count 50
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

## API Documentation

### Base URL
```
http://localhost:8000/api/v1/patients/
```

### Authentication
The API uses token-based authentication. Include the token in the Authorization header:
```
Authorization: Token <your-token>
```

### Endpoints

#### Patients
- `GET /patients/` - List all patients
- `POST /patients/` - Create new patient
- `GET /patients/{id}/` - Get patient details
- `PUT /patients/{id}/` - Update patient
- `DELETE /patients/{id}/` - Soft delete patient
- `GET /patients/statistics/` - Get patient statistics
- `GET /patients/search/` - Search patients
- `GET /patients/export/` - Export patients to CSV

#### Medical History
- `GET /medical-history/` - List medical history
- `POST /medical-history/` - Create medical history entry
- `GET /medical-history/{id}/` - Get medical history details
- `PUT /medical-history/{id}/` - Update medical history
- `DELETE /medical-history/{id}/` - Delete medical history

#### Allergies
- `GET /allergies/` - List allergies
- `POST /allergies/` - Create allergy record
- `GET /allergies/{id}/` - Get allergy details
- `PUT /allergies/{id}/` - Update allergy
- `DELETE /allergies/{id}/` - Delete allergy

#### Chronic Conditions
- `GET /chronic-conditions/` - List chronic conditions
- `POST /chronic-conditions/` - Create chronic condition
- `GET /chronic-conditions/{id}/` - Get chronic condition details
- `PUT /chronic-conditions/{id}/` - Update chronic condition
- `DELETE /chronic-conditions/{id}/` - Delete chronic condition

#### Documents
- `GET /documents/` - List documents
- `POST /documents/` - Upload document
- `GET /documents/{id}/` - Get document details
- `PUT /documents/{id}/` - Update document
- `DELETE /documents/{id}/` - Delete document
- `POST /documents/{id}/verify/` - Verify document
- `POST /documents/{id}/unverify/` - Unverify document

### Example API Usage

#### Create a Patient
```python
import requests

url = "http://localhost:8000/api/v1/patients/patients/"
headers = {
    "Authorization": "Token your-token-here",
    "Content-Type": "application/json"
}

data = {
    "first_name_en": "Ahmed",
    "first_name_ar": "أحمد",
    "last_name_en": "Al-Rashid",
    "last_name_ar": "الرشيد",
    "gender": "M",
    "date_of_birth": "1990-01-01",
    "phone_number": "+966501234567",
    "email": "ahmed@example.com",
    "address_en": "123 Main Street, Riyadh",
    "address_ar": "شارع الرئيسي 123، الرياض",
    "city": "Riyadh",
    "state_province": "Riyadh Province",
    "postal_code": "12345",
    "country": "Saudi Arabia",
    "national_id": "1234567890",
    "blood_type": "A+",
    "emergency_contact_name": "Emergency Contact",
    "emergency_contact_phone": "+966501234568",
    "emergency_contact_relationship": "Brother",
    "notes": "Test patient"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

#### Search Patients
```python
url = "http://localhost:8000/api/v1/patients/patients/search/"
params = {
    "q": "Ahmed",
    "gender": "M",
    "status": "active"
}

response = requests.get(url, params=params, headers=headers)
print(response.json())
```

## Data Models

### Patient Model
The main patient model with comprehensive fields:

```python
class Patient(models.Model):
    patient_code = models.CharField(max_length=20, unique=True)
    first_name_en = models.CharField(max_length=100)
    first_name_ar = models.CharField(max_length=100, blank=True)
    last_name_en = models.CharField(max_length=100)
    last_name_ar = models.CharField(max_length=100, blank=True)
    # ... additional fields
```

### Medical History Model
Tracks medical events and history:

```python
class MedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title_en = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200, blank=True)
    # ... additional fields
```

## Multilingual Support

The system supports both Arabic and English throughout:

- **Text Fields**: All text fields have both `_en` and `_ar` versions
- **Search**: Search works across both languages
- **API**: API responses include both language versions
- **Validation**: Input validation supports both languages

## Permissions & Security

### Role-Based Access Control
- **Administrators**: Full access to all data
- **Doctors**: Access to medical data and patient records
- **Nurses**: Access to patient records and medical data
- **Receptionists**: Access to patient registration and basic data

### Audit Logging
All operations are logged for compliance:
- Patient data access
- Medical record changes
- Document uploads
- System events
- Data exports

## Testing

Run the test suite:

```bash
python manage.py test patient_management
```

Run specific test categories:

```bash
# Model tests
python manage.py test patient_management.tests.PatientModelTests

# API tests
python manage.py test patient_management.tests.PatientAPITests

# Utility tests
python manage.py test patient_management.tests.UtilsTests
```

## Management Commands

### Create Sample Data
```bash
python manage.py create_sample_data --count 100
```

### Cleanup Old Data
```bash
python manage.py cleanup_old_data --days 365
```

## Integration Guide

### Adding to Existing Django Project

1. **Add to INSTALLED_APPS**
   ```python
   INSTALLED_APPS = [
       # ... your apps
       'patient_management',
       'audit_logs',
   ]
   ```

2. **Include URLs**
   ```python
   urlpatterns = [
       # ... your URLs
       path('api/v1/patients/', include('patient_management.urls')),
       path('api/v1/audit/', include('audit_logs.urls')),
   ]
   ```

3. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Integration with Other Modules

The patient module is designed for easy integration:

- **Appointments**: Link via `patient_id`
- **Consultations**: Access patient medical history
- **Billing**: Track patient payments
- **Insurance**: Manage patient-insurer relationships

## Configuration

### Environment Variables
```bash
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/clinic_db
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'clinic_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Performance Considerations

- **Database Indexing**: All frequently queried fields are indexed
- **Pagination**: API responses are paginated (20 items per page)
- **Caching**: Consider implementing Redis for caching
- **File Storage**: Use cloud storage for production (AWS S3, etc.)

## Security Best Practices

1. **HTTPS**: Always use HTTPS in production
2. **Token Security**: Implement token rotation
3. **File Uploads**: Validate file types and sizes
4. **Data Encryption**: Encrypt sensitive data at rest
5. **Access Logging**: Monitor all data access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Changelog

### Version 1.0.0
- Initial release
- Complete patient management functionality
- Multilingual support
- Audit logging
- API endpoints
- Admin interface
- Comprehensive testing
