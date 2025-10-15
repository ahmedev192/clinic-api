"""
Inventory views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, F, Max, Avg
from django.utils import timezone
from django.db import transaction, models
from datetime import datetime, timedelta

from .models import (
    Category, Supplier, Item, StockMovement, PurchaseOrder,
    PurchaseOrderItem, MaintenanceRecord, Alert
)
from .serializers import (
    CategorySerializer, SupplierSerializer, ItemSerializer, ItemDetailSerializer,
    StockMovementSerializer, PurchaseOrderSerializer, PurchaseOrderDetailSerializer,
    PurchaseOrderItemSerializer, MaintenanceRecordSerializer, AlertSerializer,
    ItemIntegrationSerializer, StockMovementIntegrationSerializer
)
from .filters import ItemFilter, StockMovementFilter, PurchaseOrderFilter, MaintenanceRecordFilter
from .permissions import IsInventoryAdmin, IsInventoryUser
from .reports import ReportMixin
from .integration import IntegrationMixin


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category management"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsInventoryAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name_en', 'name_ar', 'description_en', 'description_ar']
    ordering_fields = ['name_en', 'created']
    ordering = ['name_en']
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure"""
        root_categories = Category.objects.filter(parent=None, is_active=True)
        serializer = self.get_serializer(root_categories, many=True)
        return Response(serializer.data)


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet for Supplier management"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsInventoryUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name_en', 'name_ar', 'contact_person', 'email']
    ordering_fields = ['name_en', 'created']
    ordering = ['name_en']
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get items supplied by this supplier"""
        supplier = self.get_object()
        items = supplier.items.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)


class ItemViewSet(ReportMixin, IntegrationMixin, viewsets.ModelViewSet):
    """ViewSet for Item management"""
    queryset = Item.objects.all()
    permission_classes = [IsAuthenticated, IsInventoryUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ItemFilter
    search_fields = ['name_en', 'name_ar', 'code', 'description_en', 'description_ar']
    ordering_fields = ['name_en', 'current_quantity', 'created']
    ordering = ['name_en']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ItemDetailSerializer
        return ItemSerializer
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get items with low stock"""
        items = self.get_queryset().filter(current_quantity__lte=models.F('reorder_level'))
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get expired items"""
        today = timezone.now().date()
        items = self.get_queryset().filter(expiry_date__lt=today)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get items expiring soon (within 30 days)"""
        today = timezone.now().date()
        future_date = today + timedelta(days=30)
        items = self.get_queryset().filter(
            expiry_date__gte=today,
            expiry_date__lte=future_date
        )
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Adjust item stock quantity"""
        item = self.get_object()
        quantity = request.data.get('quantity', 0)
        movement_type = request.data.get('movement_type', 'adjustment')
        notes_en = request.data.get('notes_en', '')
        notes_ar = request.data.get('notes_ar', '')
        reference_number = request.data.get('reference_number', '')
        department = request.data.get('department', '')
        
        if not quantity:
            return Response(
                {'error': 'Quantity is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            previous_quantity = item.current_quantity
            new_quantity = max(0, previous_quantity + quantity)
            
            # Update item quantity
            item.current_quantity = new_quantity
            item.save()
            
            # Create stock movement record
            StockMovement.objects.create(
                item=item,
                movement_type=movement_type,
                quantity=abs(quantity),
                previous_quantity=previous_quantity,
                new_quantity=new_quantity,
                reference_number=reference_number,
                notes_en=notes_en,
                notes_ar=notes_ar,
                user=request.user,
                department=department
            )
            
            # Check for low stock alert
            if new_quantity <= item.reorder_level:
                Alert.objects.create(
                    alert_type='low_stock',
                    priority='high',
                    item=item,
                    title_en=f'Low Stock Alert: {item.name_en}',
                    title_ar=f'تنبيه مخزون منخفض: {item.name_ar}',
                    message_en=f'Item {item.name_en} is below reorder level. Current: {new_quantity}, Reorder: {item.reorder_level}',
                    message_ar=f'المادة {item.name_ar} أقل من مستوى إعادة الطلب. الحالي: {new_quantity}, إعادة الطلب: {item.reorder_level}'
                )
        
        return Response({'message': 'Stock adjusted successfully'})
    
    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """Transfer item to different location"""
        item = self.get_object()
        new_location = request.data.get('location', '')
        quantity = request.data.get('quantity', 0)
        notes_en = request.data.get('notes_en', '')
        notes_ar = request.data.get('notes_ar', '')
        
        if not new_location or not quantity:
            return Response(
                {'error': 'Location and quantity are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if quantity > item.current_quantity:
            return Response(
                {'error': 'Insufficient stock'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            previous_quantity = item.current_quantity
            new_quantity = previous_quantity - quantity
            
            # Update item quantity
            item.current_quantity = new_quantity
            item.save()
            
            # Create stock movement record
            StockMovement.objects.create(
                item=item,
                movement_type='transfer',
                quantity=quantity,
                previous_quantity=previous_quantity,
                new_quantity=new_quantity,
                notes_en=f'Transferred to {new_location}. {notes_en}',
                notes_ar=f'تم النقل إلى {new_location}. {notes_ar}',
                user=request.user,
                department=request.data.get('department', '')
            )
        
        return Response({'message': 'Item transferred successfully'})


class StockMovementViewSet(ReportMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet for StockMovement (read-only)"""
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated, IsInventoryUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = StockMovementFilter
    search_fields = ['item__name_en', 'item__name_ar', 'reference_number', 'notes_en', 'notes_ar']
    ordering_fields = ['created', 'quantity']
    ordering = ['-created']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get stock movement summary"""
        queryset = self.filter_queryset(self.get_queryset())
        
        summary = queryset.aggregate(
            total_movements=Count('id'),
            total_in=Sum('quantity', filter=Q(movement_type='in')),
            total_out=Sum('quantity', filter=Q(movement_type='out')),
        )
        
        return Response(summary)


class PurchaseOrderViewSet(ReportMixin, viewsets.ModelViewSet):
    """ViewSet for PurchaseOrder management"""
    queryset = PurchaseOrder.objects.all()
    permission_classes = [IsAuthenticated, IsInventoryUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PurchaseOrderFilter
    search_fields = ['order_number', 'supplier__name_en', 'supplier__name_ar', 'notes_en', 'notes_ar']
    ordering_fields = ['order_date', 'created', 'total_amount']
    ordering = ['-created']
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return PurchaseOrderDetailSerializer
        return PurchaseOrderSerializer
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a purchase order"""
        purchase_order = self.get_object()
        
        if purchase_order.status != 'draft':
            return Response(
                {'error': 'Only draft orders can be approved'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase_order.status = 'ordered'
        purchase_order.approved_by = request.user
        purchase_order.approved_at = timezone.now()
        purchase_order.save()
        
        return Response({'message': 'Purchase order approved successfully'})
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """Receive items from purchase order"""
        purchase_order = self.get_object()
        
        if purchase_order.status not in ['ordered', 'partial']:
            return Response(
                {'error': 'Only ordered or partially received orders can be received'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        received_items = request.data.get('received_items', [])
        
        with transaction.atomic():
            all_received = True
            
            for item_data in received_items:
                item_id = item_data.get('item_id')
                quantity_received = item_data.get('quantity_received', 0)
                
                try:
                    po_item = purchase_order.items.get(item_id=item_id)
                    po_item.quantity_received += quantity_received
                    po_item.save()
                    
                    # Update item stock
                    item = po_item.item
                    item.current_quantity += quantity_received
                    item.save()
                    
                    # Create stock movement
                    StockMovement.objects.create(
                        item=item,
                        movement_type='in',
                        quantity=quantity_received,
                        previous_quantity=item.current_quantity - quantity_received,
                        new_quantity=item.current_quantity,
                        reference_number=purchase_order.order_number,
                        notes_en=f'Received from PO {purchase_order.order_number}',
                        notes_ar=f'تم الاستلام من أمر الشراء {purchase_order.order_number}',
                        user=request.user,
                        purchase_order=purchase_order
                    )
                    
                    if po_item.quantity_received < po_item.quantity_ordered:
                        all_received = False
                        
                except PurchaseOrderItem.DoesNotExist:
                    return Response(
                        {'error': f'Item {item_id} not found in purchase order'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Update purchase order status
            if all_received:
                purchase_order.status = 'received'
                purchase_order.actual_delivery = timezone.now().date()
            else:
                purchase_order.status = 'partial'
            
            purchase_order.save()
        
        return Response({'message': 'Items received successfully'})


class MaintenanceRecordViewSet(ReportMixin, viewsets.ModelViewSet):
    """ViewSet for MaintenanceRecord management"""
    queryset = MaintenanceRecord.objects.all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [IsAuthenticated, IsInventoryUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MaintenanceRecordFilter
    search_fields = ['item__name_en', 'item__name_ar', 'technician_name', 'description_en', 'description_ar']
    ordering_fields = ['scheduled_date', 'completed_date', 'created']
    ordering = ['-scheduled_date']
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark maintenance as completed"""
        maintenance = self.get_object()
        
        if maintenance.status == 'completed':
            return Response(
                {'error': 'Maintenance is already completed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        maintenance.status = 'completed'
        maintenance.completed_date = timezone.now()
        maintenance.save()
        
        # Update item status if it was under maintenance
        if maintenance.item.status == 'maintenance':
            maintenance.item.status = 'active'
            maintenance.item.save()
        
        return Response({'message': 'Maintenance marked as completed'})
    
    @action(detail=False, methods=['get'])
    def due(self, request):
        """Get maintenance records due for service"""
        today = timezone.now().date()
        maintenance_records = self.get_queryset().filter(
            next_maintenance_date__lte=today,
            status__in=['scheduled', 'in_progress']
        )
        serializer = self.get_serializer(maintenance_records, many=True)
        return Response(serializer.data)


class AlertViewSet(ReportMixin, viewsets.ModelViewSet):
    """ViewSet for Alert management"""
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated, IsInventoryUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['alert_type', 'priority', 'is_read', 'is_resolved']
    search_fields = ['title_en', 'title_ar', 'message_en', 'message_ar']
    ordering_fields = ['created', 'priority']
    ordering = ['-created']
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark alert as read"""
        alert = self.get_object()
        alert.is_read = True
        alert.save()
        return Response({'message': 'Alert marked as read'})
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve alert"""
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save()
        return Response({'message': 'Alert resolved'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all alerts as read"""
        updated = Alert.objects.filter(is_read=False).update(is_read=True)
        return Response({'message': f'{updated} alerts marked as read'})


# Integration APIs for other modules
class ItemIntegrationViewSet(viewsets.ReadOnlyModelViewSet):
    """Integration API for other modules to access items"""
    queryset = Item.objects.filter(status='active')
    serializer_class = ItemIntegrationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['item_type', 'status']
    search_fields = ['name_en', 'name_ar', 'code']


class StockMovementIntegrationViewSet(viewsets.ModelViewSet):
    """Integration API for other modules to create stock movements"""
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementIntegrationSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create stock movement from external module"""
        item_code = request.data.get('item_code')
        quantity = request.data.get('quantity', 0)
        movement_type = request.data.get('movement_type', 'out')
        
        try:
            item = Item.objects.get(code=item_code)
        except Item.DoesNotExist:
            return Response(
                {'error': 'Item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        with transaction.atomic():
            previous_quantity = item.current_quantity
            
            if movement_type == 'out' and quantity > previous_quantity:
                return Response(
                    {'error': 'Insufficient stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            new_quantity = previous_quantity + (quantity if movement_type == 'in' else -quantity)
            
            # Update item quantity
            item.current_quantity = new_quantity
            item.save()
            
            # Create stock movement
            movement = StockMovement.objects.create(
                item=item,
                movement_type=movement_type,
                quantity=abs(quantity),
                previous_quantity=previous_quantity,
                new_quantity=new_quantity,
                reference_number=request.data.get('reference_number', ''),
                notes_en=request.data.get('notes_en', ''),
                notes_ar=request.data.get('notes_ar', ''),
                user=request.user,
                department=request.data.get('department', '')
            )
            
            serializer = self.get_serializer(movement)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
