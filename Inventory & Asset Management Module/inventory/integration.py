"""
Integration APIs for other modules
"""
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Item, StockMovement
from .serializers import ItemIntegrationSerializer, StockMovementIntegrationSerializer


class IntegrationMixin:
    """Mixin for integration functionality with other modules"""
    
    @action(detail=False, methods=['post'])
    def pharmacy_request(self, request):
        """Handle pharmacy module requests for medications and supplies"""
        try:
            items_data = request.data.get('items', [])
            department = 'Pharmacy'
            reference_number = request.data.get('reference_number', 'PHARM-REQ')
            
            movements = []
            
            with transaction.atomic():
                for item_data in items_data:
                    item_code = item_data.get('item_code')
                    quantity = item_data.get('quantity', 0)
                    notes_en = item_data.get('notes_en', 'Pharmacy request')
                    notes_ar = item_data.get('notes_ar', 'طلب صيدلية')
                    
                    try:
                        item = Item.objects.get(code=item_code)
                    except Item.DoesNotExist:
                        return Response(
                            {'error': f'Item {item_code} not found'}, 
                            status=status.HTTP_404_NOT_FOUND
                        )
                    
                    if quantity > item.current_quantity:
                        return Response(
                            {'error': f'Insufficient stock for {item_code}. Available: {item.current_quantity}, Requested: {quantity}'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Create stock movement
                    previous_quantity = item.current_quantity
                    new_quantity = previous_quantity - quantity
                    
                    item.current_quantity = new_quantity
                    item.save()
                    
                    movement = StockMovement.objects.create(
                        item=item,
                        movement_type='out',
                        quantity=quantity,
                        previous_quantity=previous_quantity,
                        new_quantity=new_quantity,
                        reference_number=reference_number,
                        notes_en=notes_en,
                        notes_ar=notes_ar,
                        user=request.user,
                        department=department
                    )
                    
                    movements.append(movement)
            
            serializer = StockMovementIntegrationSerializer(movements, many=True)
            return Response({
                'message': 'Pharmacy request processed successfully',
                'movements': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error processing pharmacy request: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def laboratory_request(self, request):
        """Handle laboratory module requests for consumables"""
        try:
            items_data = request.data.get('items', [])
            department = 'Laboratory'
            reference_number = request.data.get('reference_number', 'LAB-REQ')
            
            movements = []
            
            with transaction.atomic():
                for item_data in items_data:
                    item_code = item_data.get('item_code')
                    quantity = item_data.get('quantity', 0)
                    notes_en = item_data.get('notes_en', 'Laboratory request')
                    notes_ar = item_data.get('notes_ar', 'طلب مختبر')
                    
                    try:
                        item = Item.objects.get(code=item_code)
                    except Item.DoesNotExist:
                        return Response(
                            {'error': f'Item {item_code} not found'}, 
                            status=status.HTTP_404_NOT_FOUND
                        )
                    
                    if quantity > item.current_quantity:
                        return Response(
                            {'error': f'Insufficient stock for {item_code}. Available: {item.current_quantity}, Requested: {quantity}'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Create stock movement
                    previous_quantity = item.current_quantity
                    new_quantity = previous_quantity - quantity
                    
                    item.current_quantity = new_quantity
                    item.save()
                    
                    movement = StockMovement.objects.create(
                        item=item,
                        movement_type='out',
                        quantity=quantity,
                        previous_quantity=previous_quantity,
                        new_quantity=new_quantity,
                        reference_number=reference_number,
                        notes_en=notes_en,
                        notes_ar=notes_ar,
                        user=request.user,
                        department=department
                    )
                    
                    movements.append(movement)
            
            serializer = StockMovementIntegrationSerializer(movements, many=True)
            return Response({
                'message': 'Laboratory request processed successfully',
                'movements': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error processing laboratory request: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def billing_integration(self, request):
        """Handle billing module integration for purchase and maintenance costs"""
        try:
            integration_type = request.data.get('type')  # 'purchase' or 'maintenance'
            data = request.data.get('data', {})
            
            if integration_type == 'purchase':
                # Handle purchase order billing
                purchase_order_id = data.get('purchase_order_id')
                try:
                    from .models import PurchaseOrder
                    purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
                    
                    billing_data = {
                        'type': 'purchase',
                        'reference_id': purchase_order.id,
                        'reference_number': purchase_order.order_number,
                        'amount': float(purchase_order.total_amount),
                        'supplier': purchase_order.supplier.name_en,
                        'date': purchase_order.order_date,
                        'description_en': f'Purchase Order: {purchase_order.order_number}',
                        'description_ar': f'أمر شراء: {purchase_order.order_number}',
                        'items': []
                    }
                    
                    for item in purchase_order.items.all():
                        billing_data['items'].append({
                            'item_code': item.item.code,
                            'item_name_en': item.item.name_en,
                            'item_name_ar': item.item.name_ar,
                            'quantity': item.quantity_ordered,
                            'unit_price': float(item.unit_price),
                            'total_price': float(item.total_price)
                        })
                    
                    return Response(billing_data)
                    
                except PurchaseOrder.DoesNotExist:
                    return Response(
                        {'error': 'Purchase order not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            elif integration_type == 'maintenance':
                # Handle maintenance billing
                maintenance_id = data.get('maintenance_id')
                try:
                    from .models import MaintenanceRecord
                    maintenance = MaintenanceRecord.objects.get(id=maintenance_id)
                    
                    billing_data = {
                        'type': 'maintenance',
                        'reference_id': maintenance.id,
                        'reference_number': f'MAINT-{maintenance.id}',
                        'amount': float(maintenance.cost or 0),
                        'technician': maintenance.technician_name,
                        'date': maintenance.scheduled_date,
                        'description_en': f'Maintenance: {maintenance.item.name_en}',
                        'description_ar': f'صيانة: {maintenance.item.name_ar}',
                        'item': {
                            'code': maintenance.item.code,
                            'name_en': maintenance.item.name_en,
                            'name_ar': maintenance.item.name_ar
                        }
                    }
                    
                    return Response(billing_data)
                    
                except MaintenanceRecord.DoesNotExist:
                    return Response(
                        {'error': 'Maintenance record not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            else:
                return Response(
                    {'error': 'Invalid integration type. Must be "purchase" or "maintenance"'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Error processing billing integration: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def available_items(self, request):
        """Get available items for other modules"""
        item_type = request.query_params.get('item_type')
        department = request.query_params.get('department')
        
        queryset = Item.objects.filter(status='active', current_quantity__gt=0)
        
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        
        # Filter by department-specific item types
        if department == 'pharmacy':
            queryset = queryset.filter(item_type__in=['supply', 'consumable'])
        elif department == 'laboratory':
            queryset = queryset.filter(item_type__in=['supply', 'consumable', 'tool'])
        elif department == 'maintenance':
            queryset = queryset.filter(item_type__in=['equipment', 'tool'])
        
        serializer = ItemIntegrationSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stock_status(self, request):
        """Get stock status for specific items"""
        item_codes = request.query_params.getlist('item_codes')
        
        if not item_codes:
            return Response(
                {'error': 'item_codes parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        items = Item.objects.filter(code__in=item_codes, status='active')
        
        status_data = []
        for item in items:
            status_data.append({
                'item_code': item.code,
                'item_name_en': item.name_en,
                'item_name_ar': item.name_ar,
                'current_quantity': item.current_quantity,
                'unit': item.unit,
                'reorder_level': item.reorder_level,
                'is_low_stock': item.is_low_stock,
                'is_expired': item.is_expired,
                'location': item.location,
                'unit_cost': float(item.unit_cost or 0)
            })
        
        return Response(status_data)
