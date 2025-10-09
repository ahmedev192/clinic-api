# Clinic Analytics & Reporting Module

A comprehensive Django-based analytics and reporting module for clinic management systems, supporting both Arabic and English languages.

## Features

### 📊 Financial Reports
- Total revenue, outstanding balances, expenses, and profit summaries
- Reports by date range, department, or payment type
- Bilingual report titles and descriptions

### 👥 Patient Demographics
- Gender distribution, age ranges, and location-based insights
- Visit frequency and new vs returning patients
- Multilingual labels for data exports

### 👨‍⚕️ Doctor Performance
- Number of consultations, procedures, and generated revenue
- Average consultation time and satisfaction metrics
- Performance comparison across doctors

### 📅 Appointment Statistics
- Daily, weekly, and monthly appointment volumes
- No-show rates, cancellations, and peak hours
- Efficiency metrics and trends

### 🔧 Custom Report Builder
- Define custom report templates
- Choose modules, filters, date ranges, and aggregation fields
- Save and reuse templates for future reports
- Export data to Excel, CSV, or PDF with bilingual headers

### 🔗 Integration Ready
- Pull data from Patients, Appointments, Consultations, Billing, and Insurance modules
- Efficient data aggregation using scheduled background jobs
- Cached views for improved performance

## Technology Stack

- **Backend**: Django 4.2.7
- **API**: Django REST Framework
- **Documentation**: Swagger/OpenAPI (drf-spectacular)
- **Background Tasks**: Celery with Redis
- **Database**: PostgreSQL
- **Caching**: Redis
- **Export**: Pandas, OpenPyXL, ReportLab
- **Internationalization**: django-modeltranslation

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd analytics
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

4. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DB_NAME=clinic_analytics
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   REDIS_URL=redis://localhost:6379/0
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py setup_analytics
   python manage.py createsuperuser
   ```

6. **Start Services**
   ```bash
   # Start Redis (in a separate terminal)
   redis-server

   # Start Celery worker (in a separate terminal)
   celery -A clinic_analytics worker --loglevel=info

   # Start Celery beat for scheduled tasks (in a separate terminal)
   celery -A clinic_analytics beat --loglevel=info

   # Start Django development server
   python manage.py runserver
   ```

## API Documentation

Once the server is running, access the API documentation at:
- **Swagger UI**: http://localhost:8000/api/docs/swagger/
- **ReDoc**: http://localhost:8000/api/docs/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/docs/

## API Endpoints

### Report Templates
- `GET /api/templates/` - List all templates
- `POST /api/templates/` - Create new template
- `GET /api/templates/{id}/` - Get template details
- `PUT /api/templates/{id}/` - Update template
- `DELETE /api/templates/{id}/` - Delete template
- `POST /api/templates/{id}/duplicate/` - Duplicate template

### Report Queries
- `GET /api/queries/` - List all queries
- `POST /api/queries/` - Create new query
- `GET /api/queries/{id}/` - Get query details
- `POST /api/queries/{id}/execute/` - Execute query
- `GET /api/queries/{id}/status/` - Get query status

### Financial Reports
- `POST /api/financial/generate/` - Generate financial report
- `GET /api/financial/summary/` - Get financial summary

### Demographic Reports
- `POST /api/demographic/generate/` - Generate demographic report

### Doctor Performance
- `POST /api/doctor-performance/generate/` - Generate doctor performance report

### Appointment Statistics
- `POST /api/appointment-stats/generate/` - Generate appointment statistics

### Custom Reports
- `POST /api/custom/generate/` - Generate custom report

### Export
- `POST /api/export/generate/` - Generate export file (CSV/Excel/PDF)

## Usage Examples

### Generate Financial Report
```python
import requests

# Generate financial report for last month
response = requests.post('http://localhost:8000/api/financial/generate/', {
    'date_from': '2024-01-01T00:00:00Z',
    'date_to': '2024-01-31T23:59:59Z',
    'department': 'Cardiology',
    'payment_type': 'Insurance'
})
```

### Create Custom Report Template
```python
response = requests.post('http://localhost:8000/api/templates/', {
    'name': 'Monthly Revenue Report',
    'name_ar': 'تقرير الإيرادات الشهري',
    'description': 'Monthly revenue analysis by department',
    'description_ar': 'تحليل الإيرادات الشهري حسب القسم',
    'report_type': 'financial',
    'modules': ['billing', 'payments'],
    'filters': {'include_outstanding': True},
    'date_range': {'default_period': 'last_month'},
    'aggregation_fields': {'revenue': 'sum'},
    'group_by_fields': ['department'],
    'export_formats': ['csv', 'excel', 'pdf'],
    'include_charts': True,
    'created_by_id': 1
})
```

### Export Report to Excel
```python
response = requests.post('http://localhost:8000/api/export/generate/', {
    'query_id': 1,
    'format': 'excel',
    'include_headers_ar': True,
    'include_headers_en': True
})
```

## Background Tasks

The module uses Celery for background processing:

- **Report Generation**: Long-running reports are processed asynchronously
- **Scheduled Reports**: Automated report generation and email delivery
- **Data Cleanup**: Periodic cleanup of old reports and cache
- **Dashboard Updates**: Regular updates of dashboard data
- **External Data Sync**: Synchronization with external data sources

## Caching Strategy

- **Report Results**: Cached for 24 hours
- **Dashboard Data**: Cached for 1 hour
- **Financial Reports**: Cached for 1 hour
- **Demographic Reports**: Cached for 2 hours
- **Appointment Stats**: Cached for 30 minutes

## Internationalization

The module supports both Arabic and English:

- All model fields have Arabic translations
- Report labels and headers are bilingual
- Export files include both language headers
- API responses include translated field names

## Development

### Running Tests
```bash
python manage.py test analytics
```

### Code Quality
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 analytics/
black analytics/

# Run type checking
mypy analytics/
```

### Database Migrations
```bash
# Create migration
python manage.py makemigrations analytics

# Apply migration
python manage.py migrate
```

## Production Deployment

### Environment Variables
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DB_NAME=clinic_analytics_prod
DB_USER=your-db-user
DB_PASSWORD=your-secure-password
DB_HOST=your-db-host
REDIS_URL=redis://your-redis-host:6379/0
```

### Static Files
```bash
python manage.py collectstatic
```

### Celery Configuration
```bash
# Production Celery worker
celery -A clinic_analytics worker --loglevel=warning --concurrency=4

# Production Celery beat
celery -A clinic_analytics beat --loglevel=warning
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation

## Changelog

### Version 1.0.0
- Initial release
- Financial, demographic, and performance reports
- Custom report builder
- Bilingual support (Arabic/English)
- Export functionality (CSV, Excel, PDF)
- Background task processing
- Swagger/OpenAPI documentation
