# Clinic Inventory & Asset Management Module

A comprehensive Django-based backend system for managing medical supplies, equipment, and assets in a clinic management system. This module supports both Arabic and English languages and provides integration-ready APIs for other modules.

## Features

### Core Functionality
- **Item & Equipment Registry**: Manage medical supplies, tools, assets, and consumables
- **Stock Tracking**: Track incoming and outgoing stock movements with automatic quantity adjustments
- **Supplier Management**: Store and manage supplier information with multilingual support
- **Purchase Orders**: Create and manage purchase orders with status tracking
- **Equipment Maintenance**: Track maintenance logs and schedules for assets
- **Alert System**: Automated alerts for low stock, expiry, and maintenance due
- **Audit Trail**: Complete audit logging for all changes
- **Reports**: Comprehensive reporting for stock levels, movements, and maintenance

### Integration APIs
- **Pharmacy Integration**: APIs for medication and supply requests
- **Billing Integration**: APIs for purchase and maintenance cost tracking
- **Laboratory Integration**: APIs for lab consumable requests

### Multilingual Support
- Full Arabic and English support for all text fields
- Localized error messages and responses
- RTL-friendly data structures

## Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Run Server**
   ```bash
   python manage.py runserver
   ```

## API Documentation

Once the server is running, access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

## API Endpoints

### Items Management
- `GET /api/items/` - List all items
- `POST /api/items/` - Create new item
- `GET /api/items/{id}/` - Get item details
- `PUT /api/items/{id}/` - Update item
- `DELETE /api/items/{id}/` - Delete item
- `POST /api/items/{id}/adjust_stock/` - Adjust stock quantity
- `POST /api/items/{id}/transfer/` - Transfer item to different location
- `GET /api/items/low_stock/` - Get low stock items
- `GET /api/items/expired/` - Get expired items
- `GET /api/items/expiring_soon/` - Get items expiring soon

### Stock Movements
- `GET /api/stock-movements/` - List stock movements
- `GET /api/stock-movements/summary/` - Get movement summary

### Purchase Orders
- `GET /api/purchase-orders/` - List purchase orders
- `POST /api/purchase-orders/` - Create purchase order
- `POST /api/purchase-orders/{id}/approve/` - Approve purchase order
- `POST /api/purchase-orders/{id}/receive/` - Receive items from order

### Maintenance Records
- `GET /api/maintenance-records/` - List maintenance records
- `POST /api/maintenance-records/` - Create maintenance record
- `POST /api/maintenance-records/{id}/complete/` - Mark maintenance as completed
- `GET /api/maintenance-records/due/` - Get due maintenance

### Alerts
- `GET /api/alerts/` - List alerts
- `POST /api/alerts/{id}/mark_read/` - Mark alert as read
- `POST /api/alerts/{id}/resolve/` - Resolve alert

### Reports
- `GET /api/items/dashboard/` - Get dashboard data
- `GET /api/items/stock_levels/` - Stock levels report
- `GET /api/stock-movements/stock_movements/` - Stock movements report
- `GET /api/purchase-orders/purchase_orders/` - Purchase orders report
- `GET /api/maintenance-records/maintenance/` - Maintenance report
- `GET /api/alerts/alerts/` - Alerts report
- `GET /api/items/comprehensive/` - Comprehensive report

### Integration APIs
- `POST /api/items/pharmacy_request/` - Pharmacy module integration
- `POST /api/items/laboratory_request/` - Laboratory module integration
- `POST /api/items/billing_integration/` - Billing module integration
- `GET /api/items/available_items/` - Get available items for other modules
- `GET /api/items/stock_status/` - Get stock status for specific items

## Data Models

### Item
- Multilingual name and description fields
- Item type (supply, equipment, tool, consumable, furniture)
- Stock tracking with reorder levels
- Supplier relationships
- Status and condition tracking
- Expiry and warranty dates

### StockMovement
- Movement type (in, out, adjustment, transfer, return)
- Quantity tracking with before/after values
- User and department tracking
- Reference numbers and notes

### PurchaseOrder
- Supplier and item relationships
- Status tracking (draft, ordered, received, cancelled)
- Financial information
- Approval workflow

### MaintenanceRecord
- Maintenance type (preventive, corrective, emergency, inspection)
- Technician information
- Scheduling and completion tracking
- Cost tracking

### Alert
- Alert types (low stock, expired, expiring soon, maintenance due)
- Priority levels
- Resolution tracking

## Configuration

### Environment Variables
Create a `.env` file with the following variables:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Database
The system uses SQLite by default. For production, configure PostgreSQL or MySQL in `settings.py`.

### Celery (Optional)
For background tasks like alert checking:
```bash
celery -A clinic_inventory worker -l info
```

## Management Commands

### Check Alerts
```bash
python manage.py check_alerts
```

### Generate Report
```bash
python manage.py generate_report --start-date 2024-01-01 --end-date 2024-01-31
```

## Testing

Run the test suite:
```bash
python manage.py test inventory
```

## Permissions

The system includes role-based permissions:
- **Inventory Admin**: Full access to all functionality
- **Inventory User**: Read access and basic operations
- **Integration Access**: Limited access for other modules

## Multilingual Support

All text fields support both Arabic and English:
- Item names and descriptions
- Supplier information
- Notes and comments
- Error messages
- Report data

## Integration Examples

### Pharmacy Integration
```python
# Request items from pharmacy
response = requests.post('/api/items/pharmacy_request/', {
    'items': [
        {
            'item_code': 'SUP-001',
            'quantity': 10,
            'notes_en': 'Patient prescription',
            'notes_ar': 'وصفة طبية للمريض'
        }
    ],
    'reference_number': 'PHARM-2024-001'
})
```

### Billing Integration
```python
# Get purchase order data for billing
response = requests.post('/api/items/billing_integration/', {
    'type': 'purchase',
    'data': {
        'purchase_order_id': 123
    }
})
```

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
