# API Endpoints Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
All endpoints require authentication. Include the token in the Authorization header:
```
Authorization: Token your-token-here
```

## Consultations

### List Consultations
```http
GET /api/consultations/
```

**Query Parameters:**
- `patient_id` (int): Filter by patient ID
- `doctor_id` (int): Filter by doctor ID
- `consultation_type` (str): Filter by type (new, follow_up, emergency, routine)
- `status` (str): Filter by status (draft, in_progress, completed, cancelled)
- `consultation_date_from` (datetime): Filter from date
- `consultation_date_to` (datetime): Filter to date
- `search_text` (str): Search across text fields
- `ordering` (str): Order by field (consultation_date, created, modified)
- `page` (int): Page number for pagination

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/consultations/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "consultation_code": "CONS-ABC12345",
      "patient_id": 123,
      "doctor_id": 456,
      "appointment_id": 789,
      "consultation_type": "new",
      "status": "completed",
      "chief_complaint": {
        "en": "Chest pain",
        "ar": "ألم في الصدر"
      },
      "symptoms": {
        "en": "Sharp pain in left chest",
        "ar": "ألم حاد في الجانب الأيسر من الصدر"
      },
      "consultation_date": "2024-01-15T10:30:00Z",
      "duration_minutes": 30,
      "created_by": {
        "id": 1,
        "username": "doctor1",
        "first_name": "John",
        "last_name": "Doe"
      },
      "diagnoses": [...],
      "prescriptions": [...],
      "lab_orders": [...],
      "attachments": [...],
      "follow_up_notes": [...]
    }
  ]
}
```

### Create Consultation
```http
POST /api/consultations/
```

**Request Body:**
```json
{
  "patient_id": 123,
  "doctor_id": 456,
  "appointment_id": 789,
  "consultation_type": "new",
  "chief_complaint_en": "Chest pain",
  "chief_complaint_ar": "ألم في الصدر",
  "symptoms_en": "Sharp pain in left chest",
  "symptoms_ar": "ألم حاد في الجانب الأيسر من الصدر",
  "examination_findings_en": "Normal heart sounds",
  "examination_findings_ar": "أصوات قلب طبيعية",
  "assessment_notes_en": "Possible angina",
  "assessment_notes_ar": "احتمال ذبحة صدرية",
  "consultation_date": "2024-01-15T10:30:00Z",
  "duration_minutes": 30
}
```

### Get Consultation Details
```http
GET /api/consultations/{id}/
```

### Update Consultation
```http
PUT /api/consultations/{id}/
PATCH /api/consultations/{id}/
```

### Delete Consultation
```http
DELETE /api/consultations/{id}/
```

### Advanced Search
```http
GET /api/consultations/search/
```

**Query Parameters:**
- `patient_id` (int): Filter by patient ID
- `doctor_id` (int): Filter by doctor ID
- `consultation_type` (str): Filter by type
- `status` (str): Filter by status
- `date_from` (datetime): Filter from date
- `date_to` (datetime): Filter to date
- `search_text` (str): Search across text fields

### Get Statistics
```http
GET /api/consultations/statistics/
```

**Response:**
```json
{
  "total_consultations": 1000,
  "completed_consultations": 850,
  "draft_consultations": 50,
  "consultations_by_type": {
    "new": 600,
    "follow_up": 300,
    "emergency": 80,
    "routine": 20
  },
  "consultations_by_status": {
    "completed": 850,
    "draft": 50,
    "in_progress": 80,
    "cancelled": 20
  },
  "average_duration": 25.5,
  "total_prescriptions": 2000,
  "total_lab_orders": 1500,
  "total_attachments": 500
}
```

### Complete Consultation
```http
POST /api/consultations/{id}/complete/
```

### Add Diagnosis
```http
POST /api/consultations/{id}/add_diagnosis/
```

**Request Body:**
```json
{
  "diagnosis_id": "diagnosis-uuid",
  "status": "primary",
  "notes_en": "Confirmed diagnosis",
  "notes_ar": "تشخيص مؤكد",
  "onset_date": "2024-01-10",
  "is_resolved": false
}
```

## Diagnoses

### List Diagnoses
```http
GET /api/diagnoses/
```

**Query Parameters:**
- `category` (str): Filter by category
- `is_chronic` (bool): Filter by chronic status
- `is_contagious` (bool): Filter by contagious status
- `severity_level` (str): Filter by severity (mild, moderate, severe, critical)
- `search_text` (str): Search across text fields

### Create Diagnosis
```http
POST /api/diagnoses/
```

**Request Body:**
```json
{
  "diagnosis_code": "I25.9",
  "name_en": "Coronary artery disease",
  "name_ar": "مرض الشريان التاجي",
  "description_en": "Atherosclerotic heart disease",
  "description_ar": "مرض القلب التصلبي العصيدي",
  "category": "Cardiology",
  "is_chronic": true,
  "is_contagious": false,
  "severity_level": "moderate"
}
```

### Get Diagnoses by Category
```http
GET /api/diagnoses/by_category/
```

## Prescriptions

### List Prescriptions
```http
GET /api/prescriptions/
```

**Query Parameters:**
- `consultation_id` (uuid): Filter by consultation
- `status` (str): Filter by status (draft, active, completed, cancelled)
- `pharmacy_status` (str): Filter by pharmacy status
- `prescribed_date_from` (datetime): Filter from date
- `prescribed_date_to` (datetime): Filter to date

### Create Prescription
```http
POST /api/prescriptions/
```

**Request Body:**
```json
{
  "consultation": "consultation-uuid",
  "notes_en": "Take with food",
  "notes_ar": "تناول مع الطعام",
  "valid_until": "2024-02-15",
  "items": [
    {
      "medication_name_en": "Aspirin",
      "medication_name_ar": "أسبرين",
      "generic_name_en": "Acetylsalicylic acid",
      "generic_name_ar": "حمض الأسيتيل الساليسيليك",
      "dosage": "100mg",
      "frequency": "once_daily",
      "quantity": 30,
      "duration_days": 30,
      "instructions_en": "Take with food to avoid stomach upset",
      "instructions_ar": "تناول مع الطعام لتجنب اضطراب المعدة",
      "is_controlled_substance": false,
      "requires_refrigerator": false
    }
  ]
}
```

### Add Prescription Item
```http
POST /api/prescriptions/{id}/add_item/
```

### Send to Pharmacy
```http
POST /api/prescriptions/{id}/send_to_pharmacy/
```

**Request Body:**
```json
{
  "pharmacy_notes": "Urgent prescription"
}
```

## Lab Orders

### List Lab Orders
```http
GET /api/lab-orders/
```

**Query Parameters:**
- `consultation_id` (uuid): Filter by consultation
- `test_category` (str): Filter by test category
- `priority` (str): Filter by priority (normal, urgent, stat)
- `status` (str): Filter by status (pending, in_progress, completed, cancelled)
- `lab_status` (str): Filter by lab status

### Create Lab Order
```http
POST /api/lab-orders/
```

**Request Body:**
```json
{
  "consultation": "consultation-uuid",
  "test_name_en": "Complete Blood Count",
  "test_name_ar": "عد الدم الكامل",
  "test_category": "Blood Test",
  "priority": "normal",
  "clinical_justification_en": "Routine check-up",
  "clinical_justification_ar": "فحص روتيني",
  "requested_date": "2024-01-16T09:00:00Z"
}
```

### Add Lab Result
```http
POST /api/lab-orders/{id}/add_result/
```

**Request Body:**
```json
{
  "result_value": "4.5",
  "reference_range": "4.0-5.5",
  "unit": "million/μL",
  "status": "normal",
  "interpretation_en": "Within normal range",
  "interpretation_ar": "ضمن المعدل الطبيعي"
}
```

### Send to Laboratory
```http
POST /api/lab-orders/{id}/send_to_lab/
```

## Attachments

### List Attachments
```http
GET /api/attachments/
```

**Query Parameters:**
- `consultation_id` (uuid): Filter by consultation
- `file_type` (str): Filter by file type (image, document, lab_result, xray, scan, report, other)
- `is_confidential` (bool): Filter by confidentiality
- `access_level` (str): Filter by access level

### Upload Attachment
```http
POST /api/attachments/
```

**Request Body (multipart/form-data):**
```
file: [file]
consultation: "consultation-uuid"
file_type: "image"
title_en: "Chest X-Ray"
title_ar: "أشعة سينية للصدر"
description_en: "Frontal chest X-ray"
description_ar": "أشعة سينية أمامية للصدر"
is_confidential: true
access_level: "doctor_only"
```

## Follow-up Notes

### List Follow-up Notes
```http
GET /api/follow-up-notes/
```

**Query Parameters:**
- `consultation_id` (uuid): Filter by consultation
- `note_type` (str): Filter by type (progress, follow_up, complication, resolution, general)
- `is_urgent` (bool): Filter by urgency
- `created_by` (int): Filter by creator

### Create Follow-up Note
```http
POST /api/follow-up-notes/
```

**Request Body:**
```json
{
  "consultation": "consultation-uuid",
  "note_type": "progress",
  "content_en": "Patient showing improvement",
  "content_ar": "المريض يظهر تحسناً",
  "is_urgent": false,
  "linked_appointment_id": 123
}
```

## Audit Logs

### List Audit Logs
```http
GET /api/audit-logs/
```

**Query Parameters:**
- `model_name` (str): Filter by model name
- `action` (str): Filter by action (create, update, delete, view, upload, download)
- `user_id` (int): Filter by user

**Response:**
```json
{
  "count": 1000,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "username": "doctor1",
        "first_name": "John",
        "last_name": "Doe"
      },
      "action": "create",
      "model_name": "Consultation",
      "object_id": "consultation-uuid",
      "old_values": null,
      "new_values": {...},
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "created": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["This field is required."],
  "non_field_errors": ["Custom error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "detail": "A server error occurred."
}
```

## Pagination

All list endpoints support pagination with the following parameters:
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "count": 1000,
  "next": "http://localhost:8000/api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

## Filtering and Search

Most endpoints support:
- **Field Filtering**: Filter by specific field values
- **Date Range Filtering**: Filter by date ranges
- **Text Search**: Search across relevant text fields
- **Ordering**: Sort results by any field
- **Multilingual Search**: Search works across both English and Arabic fields

## Rate Limiting

API requests are limited to:
- 1000 requests per hour per user
- 100 requests per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```
