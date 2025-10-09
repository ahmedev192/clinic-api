# Pharmacy Management System - Backend API

A comprehensive Django REST API backend for managing pharmacy operations including medicine inventory, stock control, purchase orders, and prescription dispensing.

## Features

### 🏥 Medicine Management
- **Multilingual Support**: Full Arabic and English support for all text fields
- **Comprehensive Medicine Records**: Name, generic name, brand name, category, dosage form, strength
- **Inventory Tracking**: Reorder levels, pricing, usage instructions
- **Medicine Lifecycle**: Add, edit, deactivate, archive medicines
- **Unique Internal Codes**: Automatic tracking codes for each medicine

### 📦 Stock Control
- **Real-time Inventory**: Track available quantities for each medicine
- **Batch Management**: Track batch numbers and expiration dates
- **Automatic Alerts**: Low stock and expiration warnings
- **Stock Transactions**: Complete audit trail of all stock movements
- **FIFO Dispensing**: First In, First Out stock management

### 🛒 Purchase Orders
- **Supplier Management**: Complete supplier information and contact details
- **Order Processing**: Create, approve, order, and receive purchase orders
- **Item Tracking**: Individual item tracking with quantities and pricing
- **Status Management**: Pending, approved, ordered, received, cancelled
- **Financial Tracking**: Subtotal, tax, and total amount calculations

### 💊 Prescription Dispensing
- **Prescription Management**: Complete prescription lifecycle management
- **Dispensing Records**: Track who dispensed what and when
- **Stock Integration**: Automatic stock deduction when dispensing
- **Multilingual Notes**: Arabic and English dosage instructions
- **Partial Dispensing**: Support for partial prescription fulfillment

### 🔔 Alerts & Notifications
- **Low Stock Alerts**: Automatic alerts when stock falls below reorder level
- **Expiration Warnings**: Alerts for medicines nearing expiration
- **Expired Medicine Alerts**: Block dispensing of expired medicines
- **Alert Management**: Acknowledge and resolve alerts

### 📊 Reporting & Audit
- **Transaction Logging**: Complete audit trail for all operations
- **Stock Reports**: Current inventory, expired medicines, low stock
- **Dispensing Reports**: Daily/monthly dispensing summaries
- **Purchase History**: Complete purchase order tracking
- **User Tracking**: Track who performed each operation

## Technology Stack

- **Django 4.2.7**: Web framework
- **Django REST Framework 3.14.0**: API framework
- **drf-yasg 1.21.7**: Swagger/OpenAPI documentation
- **django-cors-headers 4.3.1**: CORS support
- **django-filter 23.3**: Advanced filtering
- **SQLite**: Database (easily configurable for PostgreSQL/MySQL)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pharmacy
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

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create sample data (optional)**
   ```bash
   python manage.py create_sample_data
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the API**
   - API Base URL: `http://localhost:8000/api/`
   - Swagger Documentation: `http://localhost:8000/api/docs/`
   - ReDoc Documentation: `http://localhost:8000/api/redoc/`

## API Endpoints

### Medicine Management
- `GET /api/medicines/` - List all medicines
- `POST /api/medicines/` - Create new medicine
- `GET /api/medicines/{id}/` - Get medicine details
- `PUT /api/medicines/{id}/` - Update medicine
- `DELETE /api/medicines/{id}/` - Delete medicine
- `GET /api/medicines/search/?q=query` - Search medicines
- `GET /api/medicines/low_stock/` - Get low stock medicines
- `GET /api/medicines/expiring_soon/` - Get expiring medicines
- `POST /api/medicines/{id}/archive/` - Archive medicine

### Stock Management
- `GET /api/stock/` - List all stock records
- `POST /api/stock/` - Create stock record
- `GET /api/stock/{id}/` - Get stock details
- `PUT /api/stock/{id}/` - Update stock
- `POST /api/stock/{id}/adjust/` - Adjust stock quantity
- `GET /api/stock/expiring_soon/` - Get expiring stock
- `GET /api/stock/expired/` - Get expired stock
- `GET /api/stock/low_stock/` - Get low stock items

### Purchase Orders
- `GET /api/purchase-orders/` - List purchase orders
- `POST /api/purchase-orders/` - Create purchase order
- `GET /api/purchase-orders/{id}/` - Get purchase order details
- `POST /api/purchase-orders/{id}/approve/` - Approve order
- `POST /api/purchase-orders/{id}/order/` - Mark as ordered
- `POST /api/purchase-orders/{id}/receive_item/` - Receive item
- `POST /api/purchase-orders/{id}/receive_all/` - Receive all items

### Prescriptions
- `GET /api/prescriptions/` - List prescriptions
- `POST /api/prescriptions/` - Create prescription
- `GET /api/prescriptions/{id}/` - Get prescription details
- `POST /api/prescriptions/{id}/dispense_item/` - Dispense item
- `GET /api/prescriptions/pending/` - Get pending prescriptions

### Alerts
- `GET /api/alerts/` - List all alerts
- `POST /api/alerts/{id}/acknowledge/` - Acknowledge alert
- `POST /api/alerts/{id}/resolve/` - Resolve alert
- `GET /api/alerts/active/` - Get active alerts

## Database Models

### Core Models
- **Category**: Medicine categories with multilingual support
- **Medicine**: Complete medicine information with multilingual fields
- **Stock**: Individual stock records with batch tracking
- **Supplier**: Supplier information and contact details
- **PurchaseOrder**: Purchase order management
- **PurchaseOrderItem**: Individual items in purchase orders
- **Prescription**: Prescription management
- **PrescriptionItem**: Individual items in prescriptions
- **DispensingRecord**: Records of dispensing operations

### Audit Models
- **StockAlert**: Stock alerts and notifications
- **StockTransaction**: Complete audit trail of stock movements

## Multilingual Support

The system provides comprehensive multilingual support for Arabic and English:

- **Medicine Names**: Both Arabic and English names
- **Generic Names**: Multilingual generic names
- **Brand Names**: Multilingual brand names
- **Categories**: Multilingual category names and descriptions
- **Notes**: Multilingual notes and instructions
- **Dosage Instructions**: Multilingual dosage instructions

## Integration Ready

The system is designed for easy integration with other modules:

- **Consultation Module**: Receive prescriptions via API
- **Billing Module**: Push dispensed medicine costs to invoices
- **User Management**: Track user operations and permissions
- **Notification Module**: Send alerts and notifications

## API Documentation

The system includes comprehensive API documentation:

- **Swagger UI**: Interactive API documentation at `/api/docs/`
- **ReDoc**: Alternative documentation at `/api/redoc/`
- **OpenAPI Schema**: Machine-readable schema at `/api/schema/`

## Authentication & Permissions

- **Session Authentication**: For web interface
- **Token Authentication**: For API access
- **User-based Permissions**: Track who performed each operation
- **Audit Trail**: Complete logging of all changes

## Sample Data

The system includes a management command to create sample data:

```bash
python manage.py create_sample_data
```

This creates:
- Sample categories and medicines
- Stock records with various expiration dates
- Sample purchase orders
- Sample prescriptions
- Test alerts and notifications

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Admin Interface
Access the Django admin at `http://localhost:8000/admin/` with the superuser credentials.

## Production Deployment

For production deployment:

1. **Update Settings**: Configure production settings
2. **Database**: Use PostgreSQL or MySQL
3. **Static Files**: Configure static file serving
4. **Security**: Update SECRET_KEY and security settings
5. **CORS**: Configure CORS for your frontend domain

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.
