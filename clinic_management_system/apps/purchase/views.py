from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Supplier, PurchaseOrder, PurchaseOrderItem
from .serializers import (
    SupplierSerializer, PurchaseOrderSerializer, PurchaseOrderCreateSerializer,
    PurchaseOrderListSerializer, PurchaseOrderItemSerializer, PurchaseOrderItemReceiveSerializer
)


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet for managing suppliers"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'contact_person', 'email', 'phone']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user"""
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active suppliers"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing purchase orders"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'status', 'order_date']
    search_fields = ['order_number', 'supplier__name', 'notes']
    ordering_fields = ['order_date', 'expected_delivery_date', 'total_amount', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        elif self.action == 'list':
            return PurchaseOrderListSerializer
        return PurchaseOrderSerializer

    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user"""
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a purchase order"""
        purchase_order = self.get_object()
        if purchase_order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be approved'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase_order.status = 'approved'
        purchase_order.updated_by = request.user
        purchase_order.save()
        
        serializer = self.get_serializer(purchase_order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def order(self, request, pk=None):
        """Mark purchase order as ordered"""
        purchase_order = self.get_object()
        if purchase_order.status not in ['pending', 'approved']:
            return Response(
                {'error': 'Only pending or approved orders can be marked as ordered'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase_order.status = 'ordered'
        purchase_order.updated_by = request.user
        purchase_order.save()
        
        serializer = self.get_serializer(purchase_order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a purchase order"""
        purchase_order = self.get_object()
        if purchase_order.status in ['received', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel received or already cancelled orders'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase_order.status = 'cancelled'
        purchase_order.updated_by = request.user
        purchase_order.save()
        
        serializer = self.get_serializer(purchase_order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def receive_item(self, request, pk=None):
        """Receive a specific item in the purchase order"""
        purchase_order = self.get_object()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        if not item_id or not quantity:
            return Response(
                {'error': 'item_id and quantity are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = purchase_order.items.get(id=item_id)
        except PurchaseOrderItem.DoesNotExist:
            return Response(
                {'error': 'Item not found in this purchase order'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if item.get_remaining_quantity() < quantity:
            return Response(
                {'error': f'Cannot receive more than remaining quantity. Remaining: {item.get_remaining_quantity()}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update item
        item.received_quantity += quantity
        item.updated_by = request.user
        item.save()
        
        # Update purchase order status
        purchase_order.update_status()
        
        serializer = self.get_serializer(purchase_order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def receive_all(self, request, pk=None):
        """Receive all items in the purchase order"""
        purchase_order = self.get_object()
        
        if purchase_order.status not in ['ordered', 'partial']:
            return Response(
                {'error': 'Only ordered or partially received orders can be fully received'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark all items as fully received
        for item in purchase_order.items.all():
            item.received_quantity = item.quantity
            item.updated_by = request.user
            item.save()
        
        # Update purchase order status
        purchase_order.mark_as_received()
        
        serializer = self.get_serializer(purchase_order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending purchase orders"""
        queryset = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue purchase orders"""
        from django.utils import timezone
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            expected_delivery_date__lt=today,
            status__in=['ordered', 'partial']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing purchase order items"""
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['purchase_order', 'medicine']
    search_fields = ['medicine__name_en', 'medicine__name_ar', 'batch_number']
    ordering_fields = ['medicine__name_en', 'quantity', 'unit_cost']
    ordering = ['medicine__name_en']

    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user"""
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """Receive this purchase order item"""
        item = self.get_object()
        serializer = PurchaseOrderItemReceiveSerializer(data=request.data)
        
        if serializer.is_valid():
            received_quantity = serializer.validated_data['received_quantity']
            batch_number = serializer.validated_data['batch_number']
            expiration_date = serializer.validated_data['expiration_date']
            notes = serializer.validated_data.get('notes', '')
            
            # Update item
            item.received_quantity += received_quantity
            item.batch_number = batch_number
            item.expiration_date = expiration_date
            if notes:
                item.notes = notes
            item.updated_by = request.user
            item.save()
            
            # Update purchase order status
            item.purchase_order.update_status()
            
            serializer = self.get_serializer(item)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
