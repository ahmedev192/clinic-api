# Clinic Management System - Consultation & Clinical Notes Module

A comprehensive Django backend module for managing medical consultations, diagnoses, prescriptions, lab requests, and follow-up notes. This module is designed for seamless integration with other clinic management system components.

## Features

### Core Functionality
- **Consultation Management**: Create, update, and track medical consultations
- **Multilingual Support**: Full Arabic and English support for all text fields
- **Diagnosis Management**: Reusable diagnosis entries with ICD-10 compatibility
- **Prescription System**: Complete prescription management with medication details
- **Lab Orders**: Laboratory and imaging test ordering system
- **File Attachments**: Secure medical file upload and management
- **Follow-up Notes**: Progress tracking and future appointment linking
- **Audit Logging**: Comprehensive audit trail for compliance

### API Features
- **RESTful API**: Complete REST API with Django REST Framework
- **Swagger Documentation**: Interactive API documentation at `/api/docs/`
- **Advanced Filtering**: Search and filter capabilities across all endpoints
- **Pagination**: Efficient data pagination for large datasets
- **Authentication**: Built-in user authentication and permissions

## Installation

### Prerequisites
- Python 3.8+
- Django 4.2+
- PostgreSQL (recommended) or SQLite (development)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd consultation
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

4. **Environment configuration**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Swagger Documentation
Access the interactive API documentation at:
```
http://localhost:8000/api/docs/
```

### Main Endpoints

#### Consultations
- `GET /api/consultations/` - List all consultations
- `POST /api/consultations/` - Create new consultation
- `GET /api/consultations/{id}/` - Get consultation details
- `PUT /api/consultations/{id}/` - Update consultation
- `DELETE /api/consultations/{id}/` - Delete consultation
- `GET /api/consultations/search/` - Advanced search
- `GET /api/consultations/statistics/` - Get statistics
- `POST /api/consultations/{id}/complete/` - Mark as completed
- `POST /api/consultations/{id}/add_diagnosis/` - Add diagnosis

#### Diagnoses
- `GET /api/diagnoses/` - List all diagnoses
- `POST /api/diagnoses/` - Create new diagnosis
- `GET /api/diagnoses/{id}/` - Get diagnosis details
- `PUT /api/diagnoses/{id}/` - Update diagnosis
- `DELETE /api/diagnoses/{id}/` - Delete diagnosis
- `GET /api/diagnoses/by_category/` - Get diagnoses by category

#### Prescriptions
- `GET /api/prescriptions/` - List all prescriptions
- `POST /api/prescriptions/` - Create new prescription
- `GET /api/prescriptions/{id}/` - Get prescription details
- `PUT /api/prescriptions/{id}/` - Update prescription
- `DELETE /api/prescriptions/{id}/` - Delete prescription
- `POST /api/prescriptions/{id}/add_item/` - Add prescription item
- `POST /api/prescriptions/{id}/send_to_pharmacy/` - Send to pharmacy

#### Lab Orders
- `GET /api/lab-orders/` - List all lab orders
- `POST /api/lab-orders/` - Create new lab order
- `GET /api/lab-orders/{id}/` - Get lab order details
- `PUT /api/lab-orders/{id}/` - Update lab order
- `DELETE /api/lab-orders/{id}/` - Delete lab order
- `POST /api/lab-orders/{id}/add_result/` - Add lab result
- `POST /api/lab-orders/{id}/send_to_lab/` - Send to laboratory

#### Attachments
- `GET /api/attachments/` - List all attachments
- `POST /api/attachments/` - Upload new attachment
- `GET /api/attachments/{id}/` - Get attachment details
- `PUT /api/attachments/{id}/` - Update attachment
- `DELETE /api/attachments/{id}/` - Delete attachment

#### Follow-up Notes
- `GET /api/follow-up-notes/` - List all follow-up notes
- `POST /api/follow-up-notes/` - Create new follow-up note
- `GET /api/follow-up-notes/{id}/` - Get follow-up note details
- `PUT /api/follow-up-notes/{id}/` - Update follow-up note
- `DELETE /api/follow-up-notes/{id}/` - Delete follow-up note

## Data Models

### Consultation
- **Primary Fields**: consultation_code, patient_id, doctor_id, appointment_id
- **Clinical Data**: Multilingual symptoms, examination findings, assessment notes
- **Status Management**: Draft, in-progress, completed, cancelled
- **Timing**: Consultation date, duration

### Diagnosis
- **Identification**: diagnosis_code (ICD-10 compatible)
- **Multilingual**: name_en, name_ar, description_en, description_ar
- **Clinical Properties**: category, severity level, chronic/contagious flags

### Prescription
- **Prescription Items**: Multiple medications per prescription
- **Multilingual**: Medication names and instructions in Arabic and English
- **Dosage Information**: Dosage, frequency, duration, quantity
- **Pharmacy Integration**: Status tracking for pharmacy module

### Lab Order
- **Test Information**: Multilingual test names and clinical justification
- **Priority Levels**: Normal, urgent, STAT
- **Laboratory Integration**: Status tracking and reference numbers

### Attachment
- **File Management**: Secure file upload and storage
- **Metadata**: Multilingual titles and descriptions
- **Security**: Confidentiality flags and access levels

## Integration Points

### Patients Module
- **Patient ID Reference**: Links consultations to patient records
- **Patient History**: Maintains consultation history per patient

### Doctors Module
- **Doctor ID Reference**: Links consultations to doctor profiles
- **Specialization**: Supports doctor specialization filtering

### Appointments Module
- **Appointment ID Reference**: Links consultations to scheduled appointments
- **Follow-up Linking**: Supports linking follow-up notes to future appointments

### Pharmacy Module
- **Prescription Status**: Tracks prescription fulfillment status
- **Medication Data**: Provides complete prescription details for dispensing

### Laboratory Module
- **Lab Order Status**: Tracks test ordering and completion
- **Result Integration**: Supports lab result attachment and review

## Multilingual Support

All text fields support both Arabic and English:
- **Suffix Convention**: `_en` for English, `_ar` for Arabic
- **API Response**: Includes both languages in structured format
- **Search**: Search works across both languages
- **Admin Interface**: Separate fields for each language

## Security Features

### Authentication
- **User Authentication**: Django's built-in authentication system
- **Permission Control**: Role-based access control
- **Session Management**: Secure session handling

### Audit Logging
- **Action Tracking**: Logs all create, update, delete operations
- **User Attribution**: Tracks which user performed each action
- **Data Changes**: Records old and new values for updates
- **Compliance**: Supports medical audit requirements

### Data Protection
- **Soft Deletion**: Maintains data integrity with soft deletes
- **Confidentiality Flags**: Marks sensitive medical information
- **Access Levels**: Controls file and data access permissions

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 consultation/

# Run type checking
mypy consultation/
```

### Database Management
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Deployment

### Production Settings
1. Set `DEBUG=False` in environment variables
2. Configure production database (PostgreSQL recommended)
3. Set up static file serving
4. Configure media file storage
5. Set up SSL/TLS encryption
6. Configure proper logging

### Environment Variables
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:password@host:port/database
```

## API Examples

### Create Consultation
```bash
curl -X POST http://localhost:8000/api/consultations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-token" \
  -d '{
    "patient_id": 123,
    "doctor_id": 456,
    "consultation_type": "new",
    "chief_complaint_en": "Chest pain",
    "chief_complaint_ar": "ألم في الصدر",
    "symptoms_en": "Sharp pain in left chest",
    "symptoms_ar": "ألم حاد في الجانب الأيسر من الصدر"
  }'
```

### Search Consultations
```bash
curl -X GET "http://localhost:8000/api/consultations/search/?patient_id=123&status=completed" \
  -H "Authorization: Token your-token"
```

### Create Prescription
```bash
curl -X POST http://localhost:8000/api/prescriptions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-token" \
  -d '{
    "consultation": "consultation-uuid",
    "notes_en": "Take with food",
    "notes_ar": "تناول مع الطعام",
    "items": [
      {
        "medication_name_en": "Aspirin",
        "medication_name_ar": "أسبرين",
        "dosage": "100mg",
        "frequency": "once_daily",
        "quantity": 30,
        "duration_days": 30
      }
    ]
  }'
```

## Support

For technical support or questions:
- Check the API documentation at `/api/docs/`
- Review the admin interface at `/admin/`
- Check the audit logs for troubleshooting

## License

This project is licensed under the MIT License - see the LICENSE file for details.
