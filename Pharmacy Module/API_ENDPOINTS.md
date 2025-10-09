# API Endpoints Reference

## Medicine Management

### Categories
- `GET /api/categories/` - List all categories
- `POST /api/categories/` - Create new category
- `GET /api/categories/{id}/` - Get category details
- `PUT /api/categories/{id}/` - Update category
- `DELETE /api/categories/{id}/` - Delete category
- `GET /api/categories/active/` - Get active categories only

### Medicines
- `GET /api/medicines/` - List all medicines
- `POST /api/medicines/` - Create new medicine
- `GET /api/medicines/{id}/` - Get medicine details
- `PUT /api/medicines/{id}/` - Update medicine
- `DELETE /api/medicines/{id}/` - Delete medicine
- `GET /api/medicines/search/?q=query` - Search medicines
- `GET /api/medicines/low_stock/` - Get medicines with low stock
- `GET /api/medicines/expiring_soon/?days=30` - Get medicines expiring soon
- `GET /api/medicines/expired/` - Get medicines with expired stock
- `POST /api/medicines/{id}/archive/` - Archive medicine
- `POST /api/medicines/{id}/unarchive/` - Unarchive medicine
- `POST /api/medicines/{id}/deactivate/` - Deactivate medicine
- `POST /api/medicines/{id}/activate/` - Activate medicine

## Stock Management

### Stock Records
- `GET /api/stock/` - List all stock records
- `POST /api/stock/` - Create stock record
- `GET /api/stock/{id}/` - Get stock details
- `PUT /api/stock/{id}/` - Update stock
- `DELETE /api/stock/{id}/` - Delete stock
- `POST /api/stock/{id}/adjust/` - Adjust stock quantity
- `GET /api/stock/expiring_soon/?days=30` - Get stock expiring soon
- `GET /api/stock/expired/` - Get expired stock
- `GET /api/stock/low_stock/` - Get low stock items

### Stock Alerts
- `GET /api/alerts/` - List all alerts
- `POST /api/alerts/` - Create alert
- `GET /api/alerts/{id}/` - Get alert details
- `PUT /api/alerts/{id}/` - Update alert
- `DELETE /api/alerts/{id}/` - Delete alert
- `POST /api/alerts/{id}/acknowledge/` - Acknowledge alert
- `POST /api/alerts/{id}/resolve/` - Resolve alert
- `GET /api/alerts/active/` - Get active alerts only
- `POST /api/alerts/acknowledge_all/` - Acknowledge all active alerts

### Stock Transactions
- `GET /api/transactions/` - List all transactions
- `GET /api/transactions/{id}/` - Get transaction details
- `GET /api/transactions/summary/` - Get transaction summary
- `GET /api/transactions/summary/?start_date=2024-01-01&end_date=2024-12-31` - Get summary for date range

## Purchase Management

### Suppliers
- `GET /api/suppliers/` - List all suppliers
- `POST /api/suppliers/` - Create new supplier
- `GET /api/suppliers/{id}/` - Get supplier details
- `PUT /api/suppliers/{id}/` - Update supplier
- `DELETE /api/suppliers/{id}/` - Delete supplier
- `GET /api/suppliers/active/` - Get active suppliers only

### Purchase Orders
- `GET /api/purchase-orders/` - List all purchase orders
- `POST /api/purchase-orders/` - Create new purchase order
- `GET /api/purchase-orders/{id}/` - Get purchase order details
- `PUT /api/purchase-orders/{id}/` - Update purchase order
- `DELETE /api/purchase-orders/{id}/` - Delete purchase order
- `POST /api/purchase-orders/{id}/approve/` - Approve purchase order
- `POST /api/purchase-orders/{id}/order/` - Mark as ordered
- `POST /api/purchase-orders/{id}/cancel/` - Cancel purchase order
- `POST /api/purchase-orders/{id}/receive_item/` - Receive specific item
- `POST /api/purchase-orders/{id}/receive_all/` - Receive all items
- `GET /api/purchase-orders/pending/` - Get pending orders
- `GET /api/purchase-orders/overdue/` - Get overdue orders

### Purchase Order Items
- `GET /api/purchase-order-items/` - List all purchase order items
- `POST /api/purchase-order-items/` - Create new item
- `GET /api/purchase-order-items/{id}/` - Get item details
- `PUT /api/purchase-order-items/{id}/` - Update item
- `DELETE /api/purchase-order-items/{id}/` - Delete item
- `POST /api/purchase-order-items/{id}/receive/` - Receive this item

## Prescription Management

### Prescriptions
- `GET /api/prescriptions/` - List all prescriptions
- `POST /api/prescriptions/` - Create new prescription
- `GET /api/prescriptions/{id}/` - Get prescription details
- `PUT /api/prescriptions/{id}/` - Update prescription
- `DELETE /api/prescriptions/{id}/` - Delete prescription
- `POST /api/prescriptions/{id}/cancel/` - Cancel prescription
- `POST /api/prescriptions/{id}/dispense_item/` - Dispense specific item
- `GET /api/prescriptions/pending/` - Get pending prescriptions
- `GET /api/prescriptions/partially_dispensed/` - Get partially dispensed prescriptions

### Prescription Items
- `GET /api/prescription-items/` - List all prescription items
- `POST /api/prescription-items/` - Create new item
- `GET /api/prescription-items/{id}/` - Get item details
- `PUT /api/prescription-items/{id}/` - Update item
- `DELETE /api/prescription-items/{id}/` - Delete item
- `POST /api/prescription-items/{id}/dispense/` - Dispense this item

### Dispensing Records
- `GET /api/dispensing-records/` - List all dispensing records
- `GET /api/dispensing-records/{id}/` - Get dispensing record details
- `GET /api/dispensing-records/by_pharmacist/?pharmacist_id=123` - Get records by pharmacist
- `GET /api/dispensing-records/by_date_range/?start_date=2024-01-01&end_date=2024-12-31` - Get records by date range

## Query Parameters

### Filtering
Most list endpoints support filtering using query parameters:
- `?category=1` - Filter by category ID
- `?is_active=true` - Filter by active status
- `?status=pending` - Filter by status
- `?supplier=1` - Filter by supplier ID
- `?medicine=1` - Filter by medicine ID

### Searching
Most list endpoints support text search:
- `?search=query` - Search in relevant text fields

### Ordering
Most list endpoints support ordering:
- `?ordering=name` - Order by name (ascending)
- `?ordering=-created_at` - Order by creation date (descending)
- `?ordering=expiration_date` - Order by expiration date

### Pagination
All list endpoints support pagination:
- `?page=1` - Get page 1
- `?page_size=20` - Set page size (default: 20)

## Response Format

All API responses follow this format:

### Success Response
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/medicines/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response
```json
{
  "field_name": ["Error message"],
  "non_field_errors": ["General error message"]
}
```

## Authentication

The API supports two authentication methods:

1. **Session Authentication**: For web interface
2. **Token Authentication**: For API access

### Token Authentication
Include the token in the Authorization header:
```
Authorization: Token your-token-here
```

## Rate Limiting

Currently no rate limiting is implemented, but it can be easily added using Django REST Framework's throttling classes.

## CORS

CORS is enabled for all origins in development. In production, configure the `CORS_ALLOWED_ORIGINS` setting.
