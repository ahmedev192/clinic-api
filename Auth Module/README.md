# Django Authentication & Authorization Backend

A comprehensive, production-ready Django authentication and authorization backend with OAuth2/OIDC SSO support, designed to be resold and deployed independently for multiple clients.

## Features

### Core Authentication
- ✅ User registration, login, logout
- ✅ Email verification
- ✅ Password reset functionality
- ✅ JWT-based authentication with refresh tokens
- ✅ Account lockout and rate limiting
- ✅ Custom password validation
- ✅ User profile management

### OAuth2/OIDC SSO Support
- ✅ Multiple OAuth2 providers (Google, Microsoft, GitHub, Okta, Auth0, Keycloak)
- ✅ Authorization Code flow with PKCE support
- ✅ OpenID Connect (OIDC) support
- ✅ Just-In-Time (JIT) user provisioning
- ✅ Account linking and unlinking
- ✅ Configurable claim mapping
- ✅ Token refresh and revocation

### Role-Based Access Control (RBAC)
- ✅ Flexible role and permission system
- ✅ User-role assignments with expiration
- ✅ Direct permission assignments
- ✅ Business-specific role configurations (LMS, HMS, Marketplace)
- ✅ Permission inheritance and delegation

### Security & Compliance
- ✅ Comprehensive audit logging
- ✅ Security event monitoring
- ✅ API access logging
- ✅ Rate limiting and DDoS protection
- ✅ CSRF protection
- ✅ XSS protection
- ✅ Secure session management

### Admin & Management
- ✅ Django Admin dashboard customization
- ✅ User, role, and permission management
- ✅ OAuth2 provider configuration
- ✅ Audit log viewing and analysis
- ✅ Security event management

### Deployment & Operations
- ✅ Docker and Docker Compose support
- ✅ Environment-based configuration
- ✅ Database migrations
- ✅ Management commands for seeding
- ✅ Health checks and monitoring
- ✅ Production-ready settings

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+
- Redis 7+

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-auth-v2
   ```

2. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - API Docs: http://localhost:8000/api/docs

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up the database**
   ```bash
   python manage.py migrate
   python manage.py seed_roles_permissions --business-type=generic
   ```

3. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Documentation

### Authentication Endpoints

#### User Registration
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}
```

#### User Login
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Password Reset Request
```http
POST /api/v1/auth/password-reset/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### Password Reset Confirm
```http
POST /api/v1/auth/password-reset/confirm/
Content-Type: application/json

{
  "token": "uuid-token",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

### OAuth2/SSO Endpoints

#### Get Available Providers
```http
GET /api/v1/oauth2/providers/
```

#### Initiate OAuth2 Flow
```http
POST /api/v1/oauth2/authorize/
Content-Type: application/json

{
  "provider_id": "provider-uuid",
  "redirect_uri": "http://localhost:3000/callback"
}
```

#### OAuth2 Callback
```http
POST /api/v1/oauth2/callback/
Content-Type: application/json

{
  "code": "authorization-code",
  "state": "state-parameter"
}
```

#### Link External Account
```http
POST /api/v1/oauth2/accounts/link/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "provider_id": "provider-uuid",
  "external_user_id": "external-user-id",
  "external_email": "user@example.com"
}
```

### Authorization Endpoints

#### Get User Permissions
```http
GET /api/v1/auth/user-permissions/
Authorization: Bearer <access-token>
```

#### Check Permission
```http
POST /api/v1/auth/check-permission/
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "permission": "user.create"
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `SECRET_KEY` | Django secret key | Required |
| `DATABASE_URL` | Database connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `EMAIL_HOST` | SMTP host | Required |
| `EMAIL_HOST_USER` | SMTP username | Required |
| `EMAIL_HOST_PASSWORD` | SMTP password | Required |
| `OAUTH_GOOGLE_CLIENT_ID` | Google OAuth2 client ID | Optional |
| `OAUTH_GOOGLE_CLIENT_SECRET` | Google OAuth2 client secret | Optional |
| `JWT_ACCESS_TOKEN_LIFETIME` | JWT access token lifetime (minutes) | `15` |
| `JWT_REFRESH_TOKEN_LIFETIME` | JWT refresh token lifetime (days) | `7` |
| `MAX_LOGIN_ATTEMPTS` | Max failed login attempts | `5` |
| `LOCKOUT_TIME` | Account lockout time (seconds) | `900` |

### Business Type Configurations

The system supports different business types with pre-configured roles and permissions:

#### LMS (Learning Management System)
- **Roles**: Super Admin, Admin, Instructor, Student, Course Admin
- **Permissions**: Course management, enrollment, assignments, grades

#### HMS (Hospital Management System)
- **Roles**: Super Admin, Admin, Doctor, Nurse, Receptionist, Patient
- **Permissions**: Patient management, appointments, medical records

#### Marketplace
- **Roles**: Super Admin, Admin, Seller, Buyer, Inventory Manager, Order Manager
- **Permissions**: Product management, orders, inventory, payments

#### Generic
- **Roles**: Super Admin, Admin, User
- **Permissions**: Basic user management and system administration

## OAuth2 Provider Setup

### Google OAuth2
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth2 credentials
5. Add redirect URI: `http://localhost:8000/api/v1/oauth2/callback/`
6. Copy Client ID and Client Secret to environment variables

### Microsoft OAuth2
1. Go to [Azure Portal](https://portal.azure.com/)
2. Register a new application
3. Add redirect URI: `http://localhost:8000/api/v1/oauth2/callback/`
4. Generate client secret
5. Copy Application ID and Client Secret to environment variables

### GitHub OAuth2
1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create new OAuth App
3. Set Authorization callback URL: `http://localhost:8000/api/v1/oauth2/callback/`
4. Copy Client ID and Client Secret to environment variables

## Management Commands

### Seed Roles and Permissions
```bash
# Generic business type
python manage.py seed_roles_permissions --business-type=generic

# LMS business type
python manage.py seed_roles_permissions --business-type=lms

# HMS business type
python manage.py seed_roles_permissions --business-type=hms

# Marketplace business type
python manage.py seed_roles_permissions --business-type=marketplace

# Clear existing data and seed
python manage.py seed_roles_permissions --business-type=generic --clear
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Run Migrations
```bash
python manage.py migrate
```

### Collect Static Files
```bash
python manage.py collectstatic
```

## Testing

### Run Tests
```bash
python manage.py test
```

### Run Specific Test
```bash
python manage.py test apps.authentication.tests.test_views
```

### Run with Coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Deployment

### Production Checklist

1. **Environment Variables**
   - Set `DEBUG=False`
   - Configure production database
   - Set secure `SECRET_KEY`
   - Configure email settings
   - Set up OAuth2 providers

2. **Security Settings**
   - Enable HTTPS
   - Configure CORS properly
   - Set up rate limiting
   - Configure logging

3. **Database**
   - Run migrations
   - Create superuser
   - Seed initial data

4. **Static Files**
   - Collect static files
   - Configure static file serving

5. **Monitoring**
   - Set up health checks
   - Configure logging
   - Set up monitoring

### Docker Production Deployment

```bash
# Build production image
docker build -t auth-backend:latest .

# Run with production settings
docker run -d \
  --name auth-backend \
  -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql://user:pass@host:port/db \
  auth-backend:latest
```

## API Integration Examples

### Frontend Integration (React)

```javascript
// Login
const login = async (email, password) => {
  const response = await fetch('/api/v1/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  if (response.ok) {
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
  }
  return data;
};

// OAuth2 Login
const oauth2Login = async (providerId) => {
  const response = await fetch('/api/v1/oauth2/authorize/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ provider_id: providerId }),
  });
  
  const data = await response.json();
  if (response.ok) {
    window.location.href = data.authorization_url;
  }
};
```

### Backend Integration (Django)

```python
# Check permissions
from django.contrib.auth.decorators import permission_required

@permission_required('user.create')
def create_user(request):
    # Your view logic
    pass

# Custom permission check
def check_permission(user, permission):
    return user.has_perm(permission)
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check database URL format
   - Ensure database is running
   - Verify credentials

2. **OAuth2 Provider Error**
   - Check client ID and secret
   - Verify redirect URI
   - Check provider configuration

3. **Email Sending Error**
   - Check SMTP settings
   - Verify email credentials
   - Check firewall settings

4. **Permission Denied Error**
   - Check user roles and permissions
   - Verify JWT token validity
   - Check API endpoint permissions

### Debug Mode

Enable debug mode for detailed error messages:

```bash
export DEBUG=True
python manage.py runserver
```

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
- Check the documentation
- Review the API documentation at `/api/docs/`

## Changelog

### Version 1.0.0
- Initial release
- Core authentication features
- OAuth2/OIDC SSO support
- RBAC system
- Admin dashboard
- Docker support
- Comprehensive documentation

