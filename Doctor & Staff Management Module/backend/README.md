# Doctor & Staff Management Module

A comprehensive Django backend module for managing clinic staff, doctors, and their schedules with full bilingual support (Arabic + English).

## Features

### Core Functionality
- **Staff Management**: Complete CRUD operations for all clinic staff
- **Doctor Profiles**: Extended profiles with medical specializations and credentials
- **Role-Based Access Control**: Flexible permission system for different staff roles
- **Schedule Management**: Working hours and availability tracking
- **Compensation Tracking**: Salary and commission management
- **Audit Logging**: Complete change tracking for compliance
- **Bilingual Support**: Full Arabic and English text support

### API Features
- **RESTful APIs**: Complete REST API with Django REST Framework
- **Swagger Documentation**: Auto-generated API documentation at `/api/docs/`
- **Advanced Search**: Multi-field search and filtering
- **Pagination**: Efficient data pagination
- **Authentication**: Token-based authentication
- **Permissions**: Role-based access control

## Quick Start

### Prerequisites
- Python 3.8+
- Django 4.2+
- pip

### Installation

1. **Clone and navigate to the project**
   ```bash
   cd clinic_management
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

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your settings
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

7. **Seed initial data (optional)**
   ```bash
   python manage.py seed_data
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - API Documentation: http://localhost:8000/api/docs/
   - Admin Panel: http://localhost:8000/admin/

## API Endpoints

### Staff Management
- `GET /api/staff/` - List all staff members
- `POST /api/staff/` - Create new staff member
- `GET /api/staff/{id}/` - Get staff details
- `PUT /api/staff/{id}/` - Update staff member
- `DELETE /api/staff/{id}/` - Delete staff member
- `GET /api/staff/search/` - Advanced search
- `GET /api/staff/stats/` - Staff statistics

### Doctor Management
- `GET /api/doctors/` - List all doctors
- `POST /api/doctors/` - Create doctor profile
- `GET /api/doctors/{id}/` - Get doctor details
- `GET /api/doctors/available/` - Get available doctors
- `GET /api/doctors/{id}/availability/` - Check doctor availability

### Schedule Management
- `GET /api/schedules/` - List all schedules
- `POST /api/schedules/` - Create schedule
- `GET /api/schedules/weekly/` - Get weekly schedule

### Roles & Specializations
- `GET /api/roles/` - List all roles
- `GET /api/specializations/` - List all specializations

## Data Models

### Staff Model
- Personal information (bilingual)
- Contact details
- Employment information
- Role assignment
- Profile image

### Doctor Model
- Medical credentials
- Specializations
- Experience details
- Consultation fees
- Availability status

### Schedule Model
- Day of week
- Start/end times
- Staff assignment
- Active status

### Role Model
- Role codes and names (bilingual)
- Permission assignments
- Active status

### Specialization Model
- Medical specializations (bilingual)
- Descriptions
- Active status

## Authentication & Permissions

### User Roles
- **Admin**: Full system access
- **Doctor**: Patient care and medical data
- **Nurse**: Limited medical data access
- **Receptionist**: Appointment and billing functions
- **Pharmacist**: Pharmacy-specific access
- **Lab Technician**: Laboratory functions

### API Authentication
```python
# Using Token Authentication
headers = {
    'Authorization': 'Token your-token-here',
    'Content-Type': 'application/json'
}
```

## Bilingual Support

All text fields support both Arabic and English:
- `name_en` / `name_ar`
- `description_en` / `description_ar`
- `address_en` / `address_ar`
- `biography_en` / `biography_ar`

## Search & Filtering

### Staff Search
```python
# Search by name, role, status, etc.
GET /api/staff/search/?query=john&role=DOC&employment_status=active
```

### Doctor Search
```python
# Search by specialization, availability, etc.
GET /api/doctors/?specialization=cardiology&is_available=true
```

### Schedule Search
```python
# Search by staff, day, time
GET /api/schedules/?staff_id=1&day_of_week=0&is_active=true
```

## Integration Points

This module is designed to integrate with:
- **Appointments Module**: Doctor availability checking
- **Patient Module**: Doctor-patient relationships
- **Billing Module**: Compensation and fee tracking
- **User Management**: Authentication and permissions

## Testing

Run the test suite:
```bash
python manage.py test staff_management
```

## Management Commands

### Seed Data
```bash
python manage.py seed_data
```
Creates sample roles, specializations, staff, and schedules.

### Clear and Reseed
```bash
python manage.py seed_data --clear
```
Clears existing data and creates fresh sample data.

## Configuration

### Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Database connection string (optional)

### Database
Default: SQLite (development)
Production: PostgreSQL or MySQL recommended

## API Documentation

Access the interactive API documentation at:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.
