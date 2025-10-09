# Laboratory Management Module

A comprehensive Django backend module for managing laboratory test workflows in a clinic management system. This module handles everything from doctor requests to result reporting and patient access, with full Arabic and English language support.

## Features

### 🧪 Lab Test Catalog
- Manage test catalog with multilingual support (Arabic/English)
- Test categories, pricing, and reference values
- Preparation instructions and descriptions
- Active/inactive test status management

### 📋 Test Requests
- Doctor-initiated test requests for patients
- Clinical notes and diagnosis in both languages
- Request status tracking (pending, collected, completed)
- Unique lab request number generation
- Urgency levels (routine, urgent, STAT)

### 🧬 Sample Collection & Tracking
- Sample collection with barcode/tracking code generation
- Collection status tracking
- Storage location and temperature monitoring
- Sample expiry management
- Batch collection support

### 📊 Results Entry & Approval
- Lab technician result entry
- Automatic abnormality flag calculation
- Critical result identification
- Supervisor/doctor approval workflow
- Result attachment support

### 📄 Report Generation
- Multilingual report generation (PDF/HTML/JSON)
- Customizable report templates
- Report delivery tracking (email, SMS, portal)
- Patient and doctor access integration

### 🔗 Integration Ready
- RESTful API endpoints for all modules
- Swagger/OpenAPI documentation
- Integration points for:
  - Consultation Module (receive requests)
  - Patient Module (attach reports)
  - Billing Module (send lab fees)

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (for background tasks)

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd "Laboratory Management Module"
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   copy env.example .env
   # Edit .env with your database and other settings
   ```

5. **Set up database:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## API Documentation

Once the server is running, access the API documentation at:
- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

## API Endpoints

### Lab Tests
- `GET /api/tests/` - List all lab tests
- `POST /api/tests/` - Create new lab test
- `GET /api/tests/{id}/` - Get specific test
- `PUT /api/tests/{id}/` - Update test
- `DELETE /api/tests/{id}/` - Delete test
- `POST /api/tests/search/` - Search tests
- `GET /api/tests/active/` - Get active tests

### Lab Requests
- `GET /api/requests/` - List all requests
- `POST /api/requests/` - Create new request
- `GET /api/requests/{id}/` - Get specific request
- `PATCH /api/requests/{id}/status/` - Update request status
- `GET /api/requests/patient/{patient_id}/` - Get requests by patient
- `GET /api/requests/doctor/{doctor_id}/` - Get requests by doctor
- `GET /api/requests/pending/` - Get pending requests

### Samples
- `GET /api/samples/` - List all samples
- `POST /api/samples/` - Create new sample
- `GET /api/samples/{id}/` - Get specific sample
- `PATCH /api/samples/{id}/status/` - Update sample status
- `POST /api/samples/search/` - Search samples
- `GET /api/samples/status/{status}/` - Get samples by status
- `GET /api/samples/expired/` - Get expired samples

### Results
- `GET /api/results/` - List all results
- `POST /api/results/` - Create new result
- `GET /api/results/{id}/` - Get specific result
- `POST /api/results/{id}/approve-reject/` - Approve/reject result
- `POST /api/results/search/` - Search results
- `GET /api/results/critical/` - Get critical results
- `GET /api/results/pending-approval/` - Get pending approval results
- `GET /api/results/patient/{patient_id}/` - Get results by patient

### Reports
- `GET /api/reports/` - List all reports
- `POST /api/reports/` - Create new report
- `GET /api/reports/{id}/` - Get specific report
- `GET /api/reports/{id}/download/` - Download report file
- `POST /api/reports/{id}/deliver/` - Deliver report
- `POST /api/reports/generate/` - Generate report from request
- `POST /api/reports/search/` - Search reports

## Multilingual Support

The system supports both Arabic and English throughout:

- All text fields have `_en` and `_ar` variants
- API responses include both language versions
- Current language is determined by Django's locale middleware
- Report generation supports both languages

## Role-Based Access

The system supports different user roles:

- **Lab Admin:** Full access to test catalog management
- **Doctor:** Can create requests and view results
- **Lab Staff:** Can collect samples and enter results
- **Supervisor:** Can approve results and manage reports
- **Patient:** Can view their own reports (via integration)

## Database Schema

### Key Models:
- `TestCategory` - Test categories (Blood, Urine, etc.)
- `LabTest` - Individual lab tests with multilingual support
- `LabRequest` - Doctor requests for lab tests
- `LabRequestItem` - Individual test items within a request
- `Sample` - Sample collection and tracking
- `LabResult` - Test results with approval workflow
- `LabReport` - Generated reports for patients
- `ReportTemplate` - Customizable report templates
- `ReportDelivery` - Report delivery tracking

## Integration Points

### Consultation Module Integration
```python
# Create lab request from consultation
POST /api/requests/
{
    "patient_id": "P12345",
    "patient_name": "John Doe",
    "patient_name_ar": "جون دو",
    "doctor_id": "D001",
    "doctor_name": "Dr. Smith",
    "clinical_notes_en": "Patient complains of...",
    "items": [
        {
            "test": 1,
            "quantity": 1,
            "notes_en": "Fasting required"
        }
    ]
}
```

### Patient Module Integration
```python
# Get patient's lab results
GET /api/results/patient/P12345/

# Get patient's reports
GET /api/reports/?patient_id=P12345
```

### Billing Module Integration
```python
# Get request total for billing
GET /api/requests/123/
# Response includes total_price field
```

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

## Production Deployment

1. Set `DEBUG=False` in environment
2. Configure proper database settings
3. Set up static file serving
4. Configure email settings for report delivery
5. Set up Redis for background tasks
6. Configure proper logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact the development team or create an issue in the repository.
