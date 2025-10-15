# Clinic Appointments & Scheduling Module

A comprehensive Django backend module for managing clinic appointments, doctor availability, waiting lists, and reminders. This module is designed to be modular, integration-ready, and production-quality with full bilingual support (Arabic and English).

## Features

### Core Functionality
- **Appointment Booking**: Create, reschedule, and cancel appointments with validation
- **Doctor Availability Management**: Define working hours, off days, and available slots
- **Waiting List Management**: Queue patients when slots are full
- **Reminder System**: Automated reminders via SMS, email, and WhatsApp
- **Audit Logging**: Complete audit trail for all appointment changes
- **Search & Filtering**: Advanced search capabilities with multiple filters

### Bilingual Support
- All text fields support both Arabic and English
- API responses include both language versions
- Admin interface displays both languages
- Reminder messages in both languages

### Integration Ready
- Modular design for easy integration with other clinic modules
- RESTful API with comprehensive documentation
- Swagger/OpenAPI documentation at `/api/docs/`
- Clean separation of concerns with service layer

## Quick Start

### Prerequisites
- Python 3.8+
- Django 4.2+
- SQLite (default) or PostgreSQL (recommended for production)

### Installation

1. **Clone and navigate to the project directory:**
   ```bash
   cd "C:\Users\Ahmed\Desktop\Appointments andScheduling"
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   copy env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   - API Documentation: http://localhost:8000/api/docs/
   - Admin Interface: http://localhost:8000/admin/
   - Health Check: http://localhost:8000/api/health/

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Main Endpoints

#### Appointments
- `GET /appointments/` - List all appointments
- `POST /appointments/` - Create new appointment
- `GET /appointments/{id}/` - Get specific appointment
- `PUT /appointments/{id}/` - Update appointment
- `DELETE /appointments/{id}/` - Delete appointment
- `POST /appointments/{id}/reschedule/` - Reschedule appointment
- `POST /appointments/{id}/cancel/` - Cancel appointment
- `POST /appointments/{id}/complete/` - Mark as completed
- `GET /appointments/search/` - Search appointments
- `GET /appointments/statistics/` - Get appointment statistics
- `GET /appointments/today/` - Get today's appointments
- `GET /appointments/upcoming/` - Get upcoming appointments

#### Doctor Availability
- `GET /doctor-availability/` - List doctor availability
- `POST /doctor-availability/` - Create availability schedule
- `GET /doctor-availability/available-slots/` - Get available time slots
- `POST /doctor-availability/block-slot/` - Block specific time slot

#### Waiting List
- `GET /waiting-list/` - List waiting list entries
- `POST /waiting-list/` - Add to waiting list
- `POST /waiting-list/{id}/promote/` - Promote to appointment
- `POST /waiting-list/{id}/contact/` - Mark as contacted

#### Reminders
- `GET /reminders/` - List reminders
- `POST /reminders/` - Create reminder
- `GET /reminders/pending/` - Get pending reminders
- `POST /reminders/{id}/mark-sent/` - Mark as sent

### Example API Usage

#### Create an Appointment
```bash
curl -X POST "http://localhost:8000/api/appointments/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "patient_id": "patient-uuid",
    "doctor_id": "doctor-uuid",
    "appointment_date": "2024-01-15",
    "appointment_time": "10:00:00",
    "reason_for_visit": {
      "en": "Regular checkup",
      "ar": "فحص دوري"
    },
    "duration_minutes": 30
  }'
```

#### Search Appointments
```bash
curl -X GET "http://localhost:8000/api/appointments/search/?patient_name=John&status=scheduled&date_from=2024-01-01" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Data Models

### Core Models

#### Appointment
- `appointment_code`: Unique identifier (e.g., APT123456)
- `patient`: Reference to patient
- `doctor`: Reference to doctor
- `appointment_date`: Date of appointment
- `appointment_time`: Time of appointment
- `status`: scheduled, confirmed, in_progress, completed, cancelled, no_show, rescheduled
- `reason_for_visit`: Bilingual text (Arabic + English)
- `notes`: Bilingual notes
- `internal_notes`: Staff-only notes

#### DoctorAvailability
- `doctor`: Reference to doctor
- `day_of_week`: 0-6 (Monday-Sunday)
- `start_time`: Working start time
- `end_time`: Working end time
- `is_recurring`: Recurring or one-time availability
- `specific_date`: For one-time availability
- `time_slot_duration`: Duration of each slot in minutes

#### WaitingList
- `patient`: Reference to patient
- `doctor`: Reference to doctor
- `preferred_date`: Preferred appointment date
- `preferred_time_start`: Preferred start time
- `preferred_time_end`: Preferred end time
- `priority`: Priority level (higher = more urgent)
- `status`: waiting, contacted, scheduled, cancelled

#### Reminder
- `appointment`: Reference to appointment
- `reminder_type`: sms, email, whatsapp, push
- `scheduled_time`: When to send reminder
- `message_template`: Bilingual message template
- `is_sent`: Whether reminder was sent
- `delivery_status`: pending, sent, delivered, failed

## Management Commands

### Send Reminders
```bash
python manage.py send_reminders
python manage.py send_reminders --dry-run  # Preview without sending
python manage.py send_reminders --limit 50  # Process only 50 reminders
```

### Cleanup Old Data
```bash
python manage.py cleanup_old_data
python manage.py cleanup_old_data --audit-log-days 180  # Keep 6 months of audit logs
python manage.py cleanup_old_data --dry-run  # Preview what would be deleted
```

## Configuration

### Clinic Settings
Configure clinic-wide settings through the admin interface or API:

- `clinic_name`: Bilingual clinic name
- `default_appointment_duration`: Default appointment duration (minutes)
- `advance_booking_days`: How many days in advance patients can book
- `reminder_hours_before`: List of hours before appointment to send reminders
- `working_hours_start/end`: Default working hours
- `timezone`: Clinic timezone
- `allow_online_booking`: Whether to allow online booking
- `require_confirmation`: Whether appointments require confirmation
- `max_appointments_per_day`: Maximum appointments per day per doctor

### Bilingual Fields
All text fields that support multiple languages use the following format:
```json
{
  "en": "English text",
  "ar": "النص العربي"
}
```

## Integration with Other Modules

### Patients Module
```python
# The system expects a Patient model with:
# - user: OneToOneField to User
# - patient_id: CharField (unique identifier)
# - phone: CharField
# - date_of_birth: DateField
# - gender: CharField
# - is_active: BooleanField
```

### Doctors Module
```python
# The system expects a Doctor model with:
# - user: OneToOneField to User
# - employee_id: CharField (unique identifier)
# - specialization: BilingualTextField
# - phone: CharField
# - is_active: BooleanField
```

### Notifications Module
The reminder system is designed to integrate with external notification services:

```python
# Example integration point
def send_reminder(reminder):
    if reminder.reminder_type == 'email':
        # Integrate with email service
        pass
    elif reminder.reminder_type == 'sms':
        # Integrate with SMS service
        pass
    elif reminder.reminder_type == 'whatsapp':
        # Integrate with WhatsApp service
        pass
```

## Testing

Run the test suite:
```bash
python manage.py test appointments
```

The test suite includes:
- Model tests
- Service layer tests
- API endpoint tests
- Integration tests

## Production Deployment

### Database
For production, use PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'clinic_appointments',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Environment Variables
Set the following environment variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Database connection string

### Static Files
```bash
python manage.py collectstatic
```

### Background Tasks
Set up a cron job or task scheduler for reminders:
```bash
# Every hour
0 * * * * /path/to/venv/bin/python /path/to/manage.py send_reminders
```

## API Authentication

The API uses Django's built-in authentication. For production, consider:
- JWT tokens
- OAuth2
- API key authentication

## Monitoring and Logging

- All actions are logged to `logs/appointments.log`
- Audit logs are stored in the database
- Health check endpoint at `/api/health/`

## Support

For questions or issues:
1. Check the API documentation at `/api/docs/`
2. Review the test cases for usage examples
3. Check the logs for error details

## License

This module is part of the Clinic Management System and follows the same license terms.
