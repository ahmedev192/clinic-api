# Patient Management API Documentation

## Overview

The Patient Management API provides comprehensive endpoints for managing patient data in a clinic management system. The API supports both Arabic and English languages and includes advanced features like search, filtering, and audit logging.

## Base URL

```
http://localhost:8000/api/v1/patients/
```

## Authentication

The API uses token-based authentication. Include your token in the Authorization header:

```
Authorization: Token <your-token>
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/v1/patients/patients/?page=2",
    "previous": null,
    "results": [...]
}
```

### Error Response
```json
{
    "field_name": ["Error message"],
    "non_field_errors": ["General error message"]
}
```

## Endpoints

### Patients

#### List Patients
```http
GET /patients/
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)
- `search` - Search query
- `gender` - Filter by gender (M, F, O)
- `status` - Filter by status (active, inactive, archived)
- `blood_type` - Filter by blood type
- `min_age` - Minimum age filter
- `max_age` - Maximum age filter
- `city` - Filter by city
- `created_after` - Filter by creation date (YYYY-MM-DD)
- `created_before` - Filter by creation date (YYYY-MM-DD)

**Response:**
```json
{
    "count": 50,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "patient_code": "PAT-2024-0001",
            "first_name_en": "Ahmed",
            "first_name_ar": "أحمد",
            "last_name_en": "Al-Rashid",
            "last_name_ar": "الرشيد",
            "full_name": "Ahmed Al-Rashid",
            "full_name_ar": "أحمد الرشيد",
            "gender": "M",
            "date_of_birth": "1990-01-01",
            "age": 34,
            "phone_number": "+966501234567",
            "email": "ahmed@example.com",
            "status": "active",
            "created_at": "2024-01-01T10:00:00Z"
        }
    ]
}
```

#### Create Patient
```http
POST /patients/
```

**Request Body:**
```json
{
    "first_name_en": "Ahmed",
    "first_name_ar": "أحمد",
    "last_name_en": "Al-Rashid",
    "last_name_ar": "الرشيد",
    "middle_name_en": "Mohammed",
    "middle_name_ar": "محمد",
    "gender": "M",
    "date_of_birth": "1990-01-01",
    "phone_number": "+966501234567",
    "secondary_phone": "+966501234568",
    "email": "ahmed@example.com",
    "address_en": "123 Main Street, Riyadh",
    "address_ar": "شارع الرئيسي 123، الرياض",
    "city": "Riyadh",
    "state_province": "Riyadh Province",
    "postal_code": "12345",
    "country": "Saudi Arabia",
    "national_id": "1234567890",
    "passport_number": "A1234567",
    "blood_type": "A+",
    "emergency_contact_name": "Emergency Contact",
    "emergency_contact_phone": "+966501234569",
    "emergency_contact_relationship": "Brother",
    "notes": "Test patient"
}
```

**Response:**
```json
{
    "id": 1,
    "patient_code": "PAT-2024-0001",
    "first_name_en": "Ahmed",
    "first_name_ar": "أحمد",
    "last_name_en": "Al-Rashid",
    "last_name_ar": "الرشيد",
    "full_name": "Ahmed Al-Rashid",
    "full_name_ar": "أحمد الرشيد",
    "gender": "M",
    "date_of_birth": "1990-01-01",
    "age": 34,
    "phone_number": "+966501234567",
    "email": "ahmed@example.com",
    "status": "active",
    "created_at": "2024-01-01T10:00:00Z",
    "created_by": 1,
    "created_by_name": "admin"
}
```

#### Get Patient Details
```http
GET /patients/{id}/
```

**Response:**
```json
{
    "id": 1,
    "patient_code": "PAT-2024-0001",
    "first_name_en": "Ahmed",
    "first_name_ar": "أحمد",
    "last_name_en": "Al-Rashid",
    "last_name_ar": "الرشيد",
    "full_name": "Ahmed Al-Rashid",
    "full_name_ar": "أحمد الرشيد",
    "gender": "M",
    "date_of_birth": "1990-01-01",
    "age": 34,
    "phone_number": "+966501234567",
    "email": "ahmed@example.com",
    "address_en": "123 Main Street, Riyadh",
    "address_ar": "شارع الرئيسي 123، الرياض",
    "city": "Riyadh",
    "state_province": "Riyadh Province",
    "postal_code": "12345",
    "country": "Saudi Arabia",
    "national_id": "1234567890",
    "passport_number": "A1234567",
    "blood_type": "A+",
    "emergency_contact_name": "Emergency Contact",
    "emergency_contact_phone": "+966501234569",
    "emergency_contact_relationship": "Brother",
    "status": "active",
    "notes": "Test patient",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z",
    "created_by": 1,
    "created_by_name": "admin",
    "updated_by": 1,
    "updated_by_name": "admin",
    "medical_history": [...],
    "allergies": [...],
    "chronic_conditions": [...],
    "documents": [...]
}
```

#### Update Patient
```http
PUT /patients/{id}/
PATCH /patients/{id}/
```

**Request Body:** Same as create patient

#### Delete Patient (Soft Delete)
```http
DELETE /patients/{id}/
```

#### Search Patients
```http
GET /patients/search/
```

**Query Parameters:**
- `q` - Search query (searches across names, phone, email, etc.)
- All other filter parameters from list patients

#### Get Patient Statistics
```http
GET /patients/statistics/
```

**Response:**
```json
{
    "total_patients": 100,
    "active_patients": 85,
    "inactive_patients": 10,
    "archived_patients": 5,
    "patients_this_month": 15,
    "total_medical_records": 500,
    "total_allergies": 200,
    "total_chronic_conditions": 150
}
```

#### Export Patients
```http
GET /patients/export/
```

**Query Parameters:**
- `include_medical` - Include medical data in export (true/false)
- All filter parameters from list patients

**Response:** CSV file download

### Medical History

#### List Medical History
```http
GET /medical-history/
```

**Query Parameters:**
- `patient` - Filter by patient ID
- `patient_code` - Filter by patient code
- `category` - Filter by category (diagnosis, surgery, treatment, etc.)
- `event_date_after` - Filter by event date (YYYY-MM-DD)
- `event_date_before` - Filter by event date (YYYY-MM-DD)
- `search` - Search query

#### Create Medical History Entry
```http
POST /medical-history/
```

**Request Body:**
```json
{
    "patient": 1,
    "category": "diagnosis",
    "title_en": "Diabetes Diagnosis",
    "title_ar": "تشخيص السكري",
    "description_en": "Patient diagnosed with Type 2 diabetes",
    "description_ar": "تم تشخيص المريض بمرض السكري من النوع الثاني",
    "diagnosis_code": "E11",
    "treatment_notes": "Prescribed metformin",
    "event_date": "2020-01-01"
}
```

### Allergies

#### List Allergies
```http
GET /allergies/
```

**Query Parameters:**
- `patient` - Filter by patient ID
- `patient_code` - Filter by patient code
- `allergy_type` - Filter by allergy type (food, medication, environmental, etc.)
- `severity` - Filter by severity (mild, moderate, severe, life_threatening)
- `search` - Search query

#### Create Allergy Record
```http
POST /allergies/
```

**Request Body:**
```json
{
    "patient": 1,
    "allergy_type": "medication",
    "allergen_en": "Penicillin",
    "allergen_ar": "البنسلين",
    "description_en": "Allergic to penicillin",
    "description_ar": "حساسية من البنسلين",
    "severity": "severe",
    "symptoms": "Rash, difficulty breathing, swelling",
    "treatment_notes": "Avoid penicillin, use alternative antibiotics",
    "first_occurrence": "2018-01-01",
    "last_occurrence": "2023-12-01"
}
```

### Chronic Conditions

#### List Chronic Conditions
```http
GET /chronic-conditions/
```

**Query Parameters:**
- `patient` - Filter by patient ID
- `patient_code` - Filter by patient code
- `condition_type` - Filter by condition type (diabetes, hypertension, etc.)
- `severity` - Filter by severity (mild, moderate, severe, critical)
- `is_active` - Filter by active status (true/false)
- `search` - Search query

#### Create Chronic Condition
```http
POST /chronic-conditions/
```

**Request Body:**
```json
{
    "patient": 1,
    "condition_type": "diabetes",
    "condition_name_en": "Type 2 Diabetes",
    "condition_name_ar": "السكري من النوع الثاني",
    "description_en": "Chronic diabetes condition",
    "description_ar": "حالة مزمنة من السكري",
    "severity": "moderate",
    "diagnosis_date": "2020-01-01",
    "icd_code": "E11",
    "current_medications": "Metformin 500mg twice daily",
    "management_plan": "Regular blood sugar monitoring, diet control",
    "notes": "Well controlled with current medication",
    "is_active": true,
    "last_review_date": "2024-01-01"
}
```

### Documents

#### List Documents
```http
GET /documents/
```

**Query Parameters:**
- `patient` - Filter by patient ID
- `patient_code` - Filter by patient code
- `document_type` - Filter by document type (id_card, passport, etc.)
- `is_verified` - Filter by verification status (true/false)
- `upload_date_after` - Filter by upload date (YYYY-MM-DD)
- `upload_date_before` - Filter by upload date (YYYY-MM-DD)
- `search` - Search query

#### Upload Document
```http
POST /documents/
```

**Request Body:** Multipart form data
- `patient` - Patient ID
- `document_type` - Document type
- `title_en` - Title in English
- `title_ar` - Title in Arabic (optional)
- `description_en` - Description in English (optional)
- `description_ar` - Description in Arabic (optional)
- `file` - File upload
- `document_date` - Date on document (YYYY-MM-DD)

#### Verify Document
```http
POST /documents/{id}/verify/
```

#### Unverify Document
```http
POST /documents/{id}/unverify/
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 405 | Method Not Allowed - HTTP method not supported |
| 500 | Internal Server Error - Server error |

## Rate Limiting

The API implements rate limiting to prevent abuse:
- 1000 requests per hour per user
- 100 requests per minute per user

## Pagination

All list endpoints support pagination:
- `page` - Page number (1-based)
- `page_size` - Items per page (default: 20, max: 100)

## Filtering

Most endpoints support filtering using query parameters:
- Exact matches: `field=value`
- Partial matches: `field__icontains=value`
- Date ranges: `field__gte=date&field__lte=date`
- Multiple values: `field=value1&field=value2`

## Search

Search functionality is available on most endpoints:
- Searches across multiple fields
- Supports both Arabic and English
- Case-insensitive
- Partial matching

## Examples

### Python Example
```python
import requests

# Set up authentication
headers = {
    'Authorization': 'Token your-token-here',
    'Content-Type': 'application/json'
}

# Create a patient
patient_data = {
    'first_name_en': 'Ahmed',
    'first_name_ar': 'أحمد',
    'last_name_en': 'Al-Rashid',
    'last_name_ar': 'الرشيد',
    'gender': 'M',
    'date_of_birth': '1990-01-01',
    'phone_number': '+966501234567',
    'national_id': '1234567890',
    'city': 'Riyadh',
    'country': 'Saudi Arabia'
}

response = requests.post(
    'http://localhost:8000/api/v1/patients/patients/',
    json=patient_data,
    headers=headers
)

if response.status_code == 201:
    patient = response.json()
    print(f"Created patient: {patient['patient_code']}")
else:
    print(f"Error: {response.json()}")
```

### JavaScript Example
```javascript
// Set up authentication
const headers = {
    'Authorization': 'Token your-token-here',
    'Content-Type': 'application/json'
};

// Search patients
const searchPatients = async (query) => {
    const response = await fetch(
        `http://localhost:8000/api/v1/patients/patients/search/?q=${query}`,
        { headers }
    );
    
    if (response.ok) {
        const data = await response.json();
        return data.results;
    } else {
        throw new Error('Search failed');
    }
};

// Usage
searchPatients('Ahmed').then(patients => {
    console.log('Found patients:', patients);
});
```

### cURL Examples

#### Create Patient
```bash
curl -X POST http://localhost:8000/api/v1/patients/patients/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name_en": "Ahmed",
    "first_name_ar": "أحمد",
    "last_name_en": "Al-Rashid",
    "last_name_ar": "الرشيد",
    "gender": "M",
    "date_of_birth": "1990-01-01",
    "phone_number": "+966501234567",
    "national_id": "1234567890",
    "city": "Riyadh",
    "country": "Saudi Arabia"
  }'
```

#### Search Patients
```bash
curl -X GET "http://localhost:8000/api/v1/patients/patients/search/?q=Ahmed&gender=M" \
  -H "Authorization: Token your-token-here"
```

#### Export Patients
```bash
curl -X GET "http://localhost:8000/api/v1/patients/patients/export/?include_medical=true" \
  -H "Authorization: Token your-token-here" \
  -o patients_export.csv
```
