# Clinic Billing & Payments Module

A comprehensive Django backend module for managing invoices, payments, refunds, and financial transactions in a clinic management system. This module is designed to be standalone and easily integrable with other clinic management modules.

## Features

### Core Functionality
- **Invoice Management**: Create, update, and track invoices with multilingual support
- **Payment Processing**: Multiple payment methods with verification and tracking
- **Refund Management**: Handle refunds with approval workflow
- **Discount System**: Flexible discount and promotion management
- **Financial Reporting**: Comprehensive financial summaries and analytics
- **Audit Trail**: Complete audit logging for all financial transactions

### Multilingual Support
- Full Arabic and English language support
- All text fields support both languages
- API responses include both language versions

### Integration Ready
- Modular design for easy integration with other modules
- RESTful API with comprehensive documentation
- Swagger/OpenAPI documentation
- Token-based authentication

## Installation

### Prerequisites
- Python 3.8+
- Django 4.2+
- PostgreSQL (recommended) or SQLite

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd billing-payments-module
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

7. **Seed initial data**
   ```bash
   python manage.py seed_data
   ```

8. **Generate sample data (optional)**
   ```bash
   python manage.py generate_sample_invoices --count 20
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Swagger Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Authentication
The API uses token-based authentication. Include the token in the Authorization header:
```
Authorization: Token your-token-here
```

## API Endpoints

### Patients
- `GET /api/patients/` - List all patients
- `POST /api/patients/` - Create a new patient
- `GET /api/patients/{id}/` - Get patient details
- `PUT /api/patients/{id}/` - Update patient
- `DELETE /api/patients/{id}/` - Delete patient
- `GET /api/patients/{id}/payment_history/` - Get patient payment history

### Doctors
- `GET /api/doctors/` - List all doctors
- `POST /api/doctors/` - Create a new doctor
- `GET /api/doctors/{id}/` - Get doctor details
- `PUT /api/doctors/{id}/` - Update doctor
- `DELETE /api/doctors/{id}/` - Delete doctor

### Services
- `GET /api/services/` - List all services
- `POST /api/services/` - Create a new service
- `GET /api/services/{id}/` - Get service details
- `PUT /api/services/{id}/` - Update service
- `DELETE /api/services/{id}/` - Delete service

### Invoices
- `GET /api/invoices/` - List all invoices
- `POST /api/invoices/` - Create a new invoice
- `GET /api/invoices/{id}/` - Get invoice details
- `PUT /api/invoices/{id}/` - Update invoice
- `DELETE /api/invoices/{id}/` - Delete invoice
- `POST /api/invoices/{id}/calculate_totals/` - Recalculate invoice totals
- `POST /api/invoices/{id}/mark_paid/` - Mark invoice as paid
- `POST /api/invoices/{id}/cancel/` - Cancel invoice
- `GET /api/invoices/overdue/` - Get overdue invoices

### Payments
- `GET /api/payments/` - List all payments
- `POST /api/payments/` - Create a new payment
- `GET /api/payments/{id}/` - Get payment details
- `PUT /api/payments/{id}/` - Update payment
- `DELETE /api/payments/{id}/` - Delete payment
- `POST /api/payments/{id}/verify/` - Verify payment
- `GET /api/payments/by_date_range/` - Get payments by date range

### Refunds
- `GET /api/refunds/` - List all refunds
- `POST /api/refunds/` - Create a new refund
- `GET /api/refunds/{id}/` - Get refund details
- `PUT /api/refunds/{id}/` - Update refund
- `DELETE /api/refunds/{id}/` - Delete refund
- `POST /api/refunds/{id}/approve/` - Approve refund
- `POST /api/refunds/{id}/process/` - Process refund

### Discounts
- `GET /api/discounts/` - List all discounts
- `POST /api/discounts/` - Create a new discount
- `GET /api/discounts/{id}/` - Get discount details
- `PUT /api/discounts/{id}/` - Update discount
- `DELETE /api/discounts/{id}/` - Delete discount
- `GET /api/discounts/valid/` - Get valid discounts
- `POST /api/discounts/{id}/apply_to_invoice/` - Apply discount to invoice

### Reports
- `GET /api/reports/summary/` - Get financial summary
- `GET /api/reports/revenue_trends/` - Get revenue trends

## Data Models

### Core Models

#### Patient
- Basic patient information with multilingual support
- Links to external patient system via `patient_id`

#### Doctor
- Doctor information with specialization
- Links to external doctor system via `doctor_id`

#### Service
- Billable services with categories
- Base pricing and service types
- Multilingual descriptions

#### Invoice
- Main billing document
- Links to patient, doctor, and services
- Financial calculations (subtotal, tax, discount, total)
- Status tracking (draft, pending, paid, cancelled)

#### InvoiceItem
- Individual line items on invoices
- Service details, quantities, pricing
- Automatic discount calculations

#### Payment
- Payment records with verification
- Multiple payment methods
- Reference numbers and notes

#### Refund
- Refund management with approval workflow
- Status tracking and processing

#### Discount
- Flexible discount system
- Percentage or fixed amount discounts
- Validity periods and usage limits

#### AuditLog
- Complete audit trail
- Tracks all financial transactions
- User and timestamp information

## Integration Guide

### With Consultation Module
```python
# When consultation is completed
from billing.models import Invoice, InvoiceItem, Service

# Create invoice for consultation
invoice = Invoice.objects.create(
    patient=consultation.patient,
    doctor=consultation.doctor,
    visit_reference=consultation.id,
    created_by=request.user
)

# Add consultation service
InvoiceItem.objects.create(
    invoice=invoice,
    service=Service.objects.get(service_type='consultation'),
    description_en=f'Consultation with {doctor.name}',
    description_ar=f'استشارة مع {doctor.name_ar}',
    quantity=1,
    unit_price=consultation.fee
)
```

### With Pharmacy Module
```python
# When prescription is filled
for medication in prescription.medications:
    InvoiceItem.objects.create(
        invoice=invoice,
        service=medication.service,
        description_en=medication.name_en,
        description_ar=medication.name_ar,
        quantity=medication.quantity,
        unit_price=medication.price
    )
```

### With Insurance Module
```python
# When insurance claim is processed
payment = Payment.objects.create(
    invoice=invoice,
    payment_method=PaymentMethod.objects.get(payment_type='insurance'),
    amount=insurance_covered_amount,
    reference_number=claim_number,
    notes_en=f'Insurance claim {claim_number}',
    notes_ar=f'مطالبة تأمين {claim_number}'
)
```

## Configuration

### Settings
Key settings in `billing_payments/settings.py`:

- `REST_FRAMEWORK`: API configuration
- `SPECTACULAR_SETTINGS`: Swagger documentation settings
- `CORS_ALLOWED_ORIGINS`: CORS configuration
- `LOGGING`: Audit logging configuration

### Multilingual Fields
All text fields support both English and Arabic:
- Format: "English text | النص العربي"
- API returns both versions in separate fields

### Tax Configuration
- Default tax rate: 15% (configurable per invoice)
- Tax calculation: `(subtotal * tax_rate) / 100`

## Testing

Run the test suite:
```bash
python manage.py test
```

Run specific test modules:
```bash
python manage.py test billing.tests.BillingModelsTestCase
python manage.py test billing.tests.BillingAPITestCase
```

## Management Commands

### Seed Data
```bash
python manage.py seed_data
```
Creates initial data including:
- Admin user
- Sample patients, doctors, services
- Payment methods
- Sample discounts

### Generate Sample Invoices
```bash
python manage.py generate_sample_invoices --count 50
```
Generates sample invoices for testing and demonstration.

## Security Considerations

- All API endpoints require authentication
- Audit logging for all financial transactions
- Input validation and sanitization
- SQL injection protection via Django ORM
- XSS protection via template escaping

## Performance Considerations

- Database indexes on frequently queried fields
- Pagination for large datasets
- Efficient queries with select_related and prefetch_related
- Caching for frequently accessed data

## Deployment

### Production Settings
1. Set `DEBUG = False`
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure logging
5. Set up monitoring and alerting

### Environment Variables
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:password@localhost:5432/billing_db
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/api/docs/`

## Changelog

### Version 1.0.0
- Initial release
- Core billing functionality
- Multilingual support
- REST API with Swagger documentation
- Audit logging
- Sample data and management commands
