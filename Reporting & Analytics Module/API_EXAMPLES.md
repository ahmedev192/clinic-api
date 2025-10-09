# API Usage Examples

This document provides practical examples of how to use the Clinic Analytics API.

## Authentication

All API endpoints require authentication. Include the authentication token in the header:

```bash
curl -H "Authorization: Token your-token-here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/templates/
```

## Report Templates

### Create a Financial Report Template

```bash
curl -X POST http://localhost:8000/api/templates/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monthly Revenue Report",
    "name_ar": "تقرير الإيرادات الشهري",
    "description": "Comprehensive monthly revenue analysis",
    "description_ar": "تحليل شامل للإيرادات الشهرية",
    "report_type": "financial",
    "modules": ["billing", "payments"],
    "filters": {
      "include_outstanding": true,
      "include_breakdown": true
    },
    "date_range": {
      "default_period": "last_month",
      "custom_range": true
    },
    "aggregation_fields": {
      "revenue": "sum",
      "expenses": "sum"
    },
    "group_by_fields": ["department", "payment_type"],
    "export_formats": ["csv", "excel", "pdf"],
    "include_charts": true,
    "created_by_id": 1
  }'
```

### List All Templates

```bash
curl -X GET http://localhost:8000/api/templates/ \
  -H "Authorization: Token your-token-here"
```

### Duplicate a Template

```bash
curl -X POST http://localhost:8000/api/templates/1/duplicate/ \
  -H "Authorization: Token your-token-here"
```

## Financial Reports

### Generate Financial Report

```bash
curl -X POST http://localhost:8000/api/financial/generate/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-31T23:59:59Z",
    "department": "Cardiology",
    "payment_type": "Insurance"
  }'
```

### Get Financial Summary

```bash
curl -X GET "http://localhost:8000/api/financial/summary/?days=30" \
  -H "Authorization: Token your-token-here"
```

## Demographic Reports

### Generate Demographic Report

```bash
curl -X POST http://localhost:8000/api/demographic/generate/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-31T23:59:59Z",
    "include_gender": true,
    "include_age_groups": true,
    "include_location": true,
    "include_visit_frequency": true
  }'
```

## Doctor Performance Reports

### Generate Doctor Performance Report

```bash
curl -X POST http://localhost:8000/api/doctor-performance/generate/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-31T23:59:59Z",
    "doctor_ids": [1, 2, 3],
    "include_revenue": true,
    "include_consultation_time": true,
    "include_satisfaction": false
  }'
```

## Appointment Statistics

### Generate Appointment Statistics

```bash
curl -X POST http://localhost:8000/api/appointment-stats/generate/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-31T23:59:59Z",
    "group_by": "day",
    "include_no_shows": true,
    "include_cancellations": true,
    "include_peak_hours": true
  }'
```

## Custom Reports

### Generate Custom Report

```bash
curl -X POST http://localhost:8000/api/custom/generate/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Custom Patient Analysis",
    "name_ar": "تحليل مخصص للمرضى",
    "modules": ["patients", "appointments"],
    "filters": {
      "status": "active",
      "age_min": 18,
      "age_max": 65
    },
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-01-31T23:59:59Z",
    "group_by_fields": ["department", "gender"],
    "aggregation_fields": {
      "count": "count",
      "avg_age": "avg"
    },
    "export_formats": ["csv", "excel"],
    "save_template": true
  }'
```

## Report Queries

### Create Report Query

```bash
curl -X POST http://localhost:8000/api/queries/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Q1 Financial Report",
    "name_ar": "تقرير مالي للربع الأول",
    "report_type": "financial",
    "filters": {
      "department": "Cardiology",
      "payment_type": "Insurance"
    },
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-03-31T23:59:59Z",
    "group_by": ["department", "month"],
    "aggregation": {
      "revenue": "sum",
      "count": "count"
    },
    "created_by_id": 1
  }'
```

### Execute Report Query

```bash
curl -X POST http://localhost:8000/api/queries/1/execute/ \
  -H "Authorization: Token your-token-here"
```

### Check Query Status

```bash
curl -X GET http://localhost:8000/api/queries/1/status/ \
  -H "Authorization: Token your-token-here"
```

## Export Reports

### Export to CSV

```bash
curl -X POST http://localhost:8000/api/export/generate/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": 1,
    "format": "csv",
    "include_headers_ar": true,
    "include_headers_en": true
  }' \
  --output report.csv
```

### Export to Excel

```bash
curl -X POST http://localhost:8000/api/export/generate/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": 1,
    "format": "excel",
    "include_headers_ar": true,
    "include_headers_en": true
  }' \
  --output report.xlsx
```

### Export to PDF

```bash
curl -X POST http://localhost:8000/api/export/generate/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": 1,
    "format": "pdf",
    "include_headers_ar": true,
    "include_headers_en": true
  }' \
  --output report.pdf
```

## Data Sources

### Create Data Source

```bash
curl -X POST http://localhost:8000/api/data-sources/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Insurance API",
    "name_ar": "واجهة برمجة التأمين",
    "source_type": "api",
    "connection_config": {
      "base_url": "https://api.insurance.com",
      "api_key": "your-api-key",
      "timeout": 30
    },
    "is_active": true
  }'
```

## Report Schedules

### Create Scheduled Report

```bash
curl -X POST http://localhost:8000/api/schedules/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Financial Report",
    "name_ar": "تقرير مالي يومي",
    "template_id": 1,
    "frequency": "daily",
    "time": "09:00:00",
    "recipients": ["admin@clinic.com", "manager@clinic.com"],
    "is_active": true,
    "created_by_id": 1
  }'
```

## Python Client Examples

### Using requests library

```python
import requests
import json

# Base URL and authentication
BASE_URL = "http://localhost:8000/api"
HEADERS = {
    "Authorization": "Token your-token-here",
    "Content-Type": "application/json"
}

# Generate financial report
def generate_financial_report(date_from, date_to, department=None):
    url = f"{BASE_URL}/financial/generate/"
    data = {
        "date_from": date_from,
        "date_to": date_to
    }
    if department:
        data["department"] = department
    
    response = requests.post(url, headers=HEADERS, json=data)
    return response.json()

# Create custom report
def create_custom_report(name, modules, date_from, date_to):
    url = f"{BASE_URL}/custom/generate/"
    data = {
        "name": name,
        "modules": modules,
        "date_from": date_from,
        "date_to": date_to,
        "export_formats": ["csv", "excel"]
    }
    
    response = requests.post(url, headers=HEADERS, json=data)
    return response.json()

# Export report
def export_report(query_id, format_type):
    url = f"{BASE_URL}/export/generate/"
    data = {
        "query_id": query_id,
        "format": format_type,
        "include_headers_ar": True,
        "include_headers_en": True
    }
    
    response = requests.post(url, headers=HEADERS, json=data)
    return response.content  # Binary content for file download
```

### Using Django REST Framework client

```python
from rest_framework.test import APIClient
from django.contrib.auth.models import User

# Setup
client = APIClient()
user = User.objects.get(username='admin')
client.force_authenticate(user=user)

# Generate demographic report
response = client.post('/api/demographic/generate/', {
    'date_from': '2024-01-01T00:00:00Z',
    'date_to': '2024-01-31T23:59:59Z',
    'include_gender': True,
    'include_age_groups': True
})

print(response.data)
```

## Error Handling

### Common Error Responses

```json
{
  "error": "Query must be completed before export.",
  "detail": "The requested query is still processing."
}
```

```json
{
  "date_from": ["Date from cannot be in the future."],
  "date_to": ["Date to cannot be in the future."]
}
```

### Handling Errors in Python

```python
import requests

def safe_api_call(url, data):
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    return None
```

## Pagination

### List with Pagination

```bash
curl -X GET "http://localhost:8000/api/templates/?page=2&page_size=10" \
  -H "Authorization: Token your-token-here"
```

### Response Format

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/templates/?page=3",
  "previous": "http://localhost:8000/api/templates/?page=1",
  "results": [...]
}
```

## Filtering and Searching

### Filter by Report Type

```bash
curl -X GET "http://localhost:8000/api/templates/?report_type=financial" \
  -H "Authorization: Token your-token-here"
```

### Search by Name

```bash
curl -X GET "http://localhost:8000/api/templates/?search=monthly" \
  -H "Authorization: Token your-token-here"
```

### Order by Created Date

```bash
curl -X GET "http://localhost:8000/api/templates/?ordering=-created_at" \
  -H "Authorization: Token your-token-here"
```

## Rate Limiting

The API implements rate limiting to prevent abuse. If you exceed the rate limit, you'll receive a 429 status code:

```json
{
  "detail": "Request was throttled. Expected available in 60 seconds."
}
```

## Webhook Integration

### Configure Webhook for Report Completion

```python
# In your Django settings
WEBHOOK_URLS = {
    'report_completed': 'https://your-app.com/webhooks/report-completed/',
    'report_failed': 'https://your-app.com/webhooks/report-failed/'
}
```

### Webhook Payload Example

```json
{
  "event": "report_completed",
  "query_id": 123,
  "template_id": 45,
  "status": "completed",
  "completed_at": "2024-01-15T10:30:00Z",
  "download_url": "https://api.clinic.com/api/export/generate/"
}
```
