# Admin Dashboard Module - Clinic Management System

A comprehensive admin dashboard module for the Clinic Management System, built with Django and PostgreSQL. This module provides centralized administration, monitoring, analytics, and integration capabilities for all clinic modules.

## Features

### 🏥 Dashboard Overview
- Real-time statistics and KPIs
- Role-based dashboard configurations
- Customizable widgets and quick actions
- Multi-language support (English/Arabic)

### 📊 System Monitoring
- Health checks for all modules
- Performance metrics tracking
- Error logging and alerting
- Module connectivity monitoring

### 📈 Analytics & Reporting
- Comprehensive reporting system
- Data visualization and charts
- Scheduled report generation
- Export capabilities (CSV, Excel, PDF)

### 🔔 Notifications
- Real-time notification system
- Alert thresholds and rules
- Multi-channel delivery (Dashboard, Email, SMS)
- Notification templates and subscriptions

### 🔍 Audit & Compliance
- Complete audit trail logging
- Security event tracking
- Data access monitoring
- Compliance reporting (HIPAA, GDPR, SOX)

### 🔗 Module Integration
- API call management
- Data synchronization
- Webhook endpoints
- Integration testing framework

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (for background tasks)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd admin-dashboard
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
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py setup_dashboard
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/admin_dashboard_db

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Module Integration URLs
AUTH_MODULE_URL=http://localhost:8001/api/
PATIENT_MODULE_URL=http://localhost:8002/api/
DOCTOR_MODULE_URL=http://localhost:8003/api/
APPOINTMENT_MODULE_URL=http://localhost:8004/api/
CONSULTATION_MODULE_URL=http://localhost:8005/api/
BILLING_MODULE_URL=http://localhost:8006/api/
PHARMACY_MODULE_URL=http://localhost:8007/api/
LABORATORY_MODULE_URL=http://localhost:8008/api/
INVENTORY_MODULE_URL=http://localhost:8009/api/
REPORTING_MODULE_URL=http://localhost:8010/api/

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Language Settings
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,ar
```

### Module Integration

The admin dashboard is designed to integrate with other clinic modules. Configure the module URLs in your environment file to enable data aggregation and monitoring.

## API Documentation

### Swagger/OpenAPI
Access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

### Key Endpoints

#### Dashboard
- `GET /api/overview/` - Dashboard overview statistics
- `GET /api/role-based-data/` - Role-based data access
- `GET /api/real-time-metrics/` - Real-time metrics

#### Monitoring
- `GET /api/monitoring/status/` - System health status
- `GET /api/monitoring/health/` - Component health checks
- `GET /api/monitoring/alerts/` - System alerts

#### Analytics
- `GET /api/analytics/summary/` - Analytics summary
- `GET /api/analytics/chart-data/` - Chart data
- `POST /api/analytics/reports/generate/` - Generate reports

#### Notifications
- `GET /api/notifications/summary/` - Notification summary
- `POST /api/notifications/send/` - Send notification
- `GET /api/notifications/thresholds/` - Alert thresholds

#### Audit
- `GET /api/audit/summary/` - Audit summary
- `GET /api/audit/logs/` - Audit logs
- `POST /api/audit/compliance-reports/generate/` - Generate compliance report

#### Integration
- `GET /api/integration/summary/` - Integration summary
- `GET /api/integration/status/` - Module connection status
- `POST /api/integration/connections/{id}/test/` - Test module connection

## User Roles

The system supports the following user roles with different access levels:

### Super Admin
- Full system access
- All module management
- System configuration
- Audit and compliance

### Admin
- Most system access
- User management
- Module monitoring
- Limited system configuration

### Accountant
- Billing and financial data
- Revenue reports
- Payment processing
- Financial analytics

### Doctor
- Patient data access
- Appointment management
- Consultation records
- Limited reporting

### Receptionist
- Patient management
- Appointment scheduling
- Basic reporting
- Communication tools

### Nurse
- Patient care data
- Appointment assistance
- Basic patient information
- Limited system access

## Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.dashboard
python manage.py test apps.monitoring
python manage.py test apps.analytics
python manage.py test apps.notifications
python manage.py test apps.audit
python manage.py test apps.integration
```

### Test Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Background Tasks

The system uses Celery for background tasks:

### Start Celery Worker
```bash
celery -A admin_dashboard worker -l info
```

### Start Celery Beat (for scheduled tasks)
```bash
celery -A admin_dashboard beat -l info
```

### Background Tasks Include:
- Health check monitoring
- Data synchronization
- Report generation
- Notification processing
- Log cleanup

## Deployment

### Production Settings
1. Set `DEBUG=False`
2. Configure proper database credentials
3. Set up Redis for background tasks
4. Configure static file serving
5. Set up SSL certificates
6. Configure proper logging

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Environment-specific Configuration
- Development: Use SQLite and local Redis
- Staging: Use PostgreSQL and Redis with limited resources
- Production: Use PostgreSQL cluster and Redis cluster

## Security

### Authentication
- Django's built-in authentication system
- Token-based API authentication
- Role-based access control

### Data Protection
- All API endpoints require authentication
- Sensitive data is encrypted
- Audit logging for all actions
- GDPR compliance features

### Network Security
- CORS configuration
- IP whitelisting (configurable)
- Rate limiting
- Request validation

## Monitoring & Maintenance

### Health Checks
- Database connectivity
- Redis connectivity
- Module API availability
- System resource usage

### Log Management
- Centralized logging
- Log rotation
- Error tracking
- Performance monitoring

### Backup Strategy
- Database backups
- Configuration backups
- Log file archiving
- Disaster recovery procedures

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check PostgreSQL service
   - Verify connection string
   - Check firewall settings

2. **Module Integration Issues**
   - Verify module URLs
   - Check network connectivity
   - Review authentication settings

3. **Performance Issues**
   - Monitor database queries
   - Check Redis connectivity
   - Review background task queue

4. **Notification Issues**
   - Check notification templates
   - Verify user subscriptions
   - Review alert thresholds

### Logs Location
- Application logs: `logs/admin_dashboard.log`
- Error logs: Django error logs
- System logs: System-specific locations

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
- Check the documentation

## Changelog

### Version 1.0.0
- Initial release
- Core dashboard functionality
- Module integration framework
- Analytics and reporting
- Notification system
- Audit and compliance features
