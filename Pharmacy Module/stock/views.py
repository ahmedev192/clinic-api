from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Stock, StockAlert, StockTransaction
from .serializers import (
    StockSerializer, StockListSerializer, StockAlertSerializer,
    StockTransactionSerializer, StockAdjustmentSerializer
)
from medicine.models import Medicine


class StockViewSet(viewsets.ModelViewSet):
    """ViewSet for managing stock records"""
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['medicine', 'is_active', 'stock_type', 'expiration_date']
    search_fields = ['medicine__name_en', 'medicine__name_ar', 'batch_number']
    ordering_fields = ['expiration_date', 'quantity', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return StockListSerializer
        return StockSerializer

    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user"""
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get stock expiring within specified days"""
        days = int(request.query_params.get('days', 30))
        future_date = timezone.now().date() + timedelta(days=days)
        
        queryset = self.get_queryset().filter(
            is_active=True,
            expiration_date__lte=future_date,
            expiration_date__gte=timezone.now().date()
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get expired stock"""
        queryset = self.get_queryset().filter(
            is_active=True,
            expiration_date__lt=timezone.now().date()
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get stock for medicines below reorder level"""
        medicines = Medicine.objects.filter(is_active=True, is_archived=False)
        low_stock_medicines = [medicine for medicine in medicines if medicine.is_low_stock()]
        
        # Get stock records for low stock medicines
        queryset = self.get_queryset().filter(
            medicine__in=low_stock_medicines,
            is_active=True
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def adjust(self, request, pk=None):
        """Adjust stock quantity"""
        stock = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity_change = serializer.validated_data['quantity_change']
            notes = serializer.validated_data.get('notes', '')
            reference_number = serializer.validated_data.get('reference_number', '')
            reference_type = serializer.validated_data.get('reference_type', 'adjustment')
            
            # Record transaction
            StockTransaction.objects.create(
                medicine=stock.medicine,
                stock_record=stock,
                transaction_type='adjustment',
                quantity_change=quantity_change,
                quantity_before=stock.quantity,
                quantity_after=stock.quantity + quantity_change,
                reference_number=reference_number,
                reference_type=reference_type,
                notes=notes,
                created_by=request.user
            )
            
            # Update stock quantity
            stock.quantity += quantity_change
            stock.updated_by = request.user
            stock.save()
            
            # Check for alerts
            self._check_stock_alerts(stock)
            
            serializer = self.get_serializer(stock)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _check_stock_alerts(self, stock):
        """Check and create stock alerts"""
        medicine = stock.medicine
        
        # Check for low stock alert
        if medicine.is_low_stock():
            StockAlert.objects.get_or_create(
                medicine=medicine,
                stock_record=stock,
                alert_type='low_stock',
                status='active',
                defaults={
                    'message': f'Low stock alert: {medicine.name_en} has {stock.quantity} units remaining (reorder level: {medicine.reorder_level})',
                    'threshold_value': medicine.reorder_level,
                    'actual_value': stock.quantity,
                    'created_by': self.request.user
                }
            )


class StockAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for managing stock alerts"""
    queryset = StockAlert.objects.all()
    serializer_class = StockAlertSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['medicine', 'alert_type', 'status']
    search_fields = ['medicine__name_en', 'medicine__name_ar', 'message']
    ordering_fields = ['created_at', 'alert_type']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        alert.acknowledge(request.user)
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        alert.resolve()
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active alerts"""
        queryset = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def acknowledge_all(self, request):
        """Acknowledge all active alerts"""
        queryset = self.get_queryset().filter(status='active')
        updated_count = queryset.update(
            status='acknowledged',
            acknowledged_by=request.user,
            acknowledged_at=timezone.now()
        )
        return Response({'message': f'{updated_count} alerts acknowledged'})


class StockTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing stock transactions (read-only)"""
    queryset = StockTransaction.objects.all()
    serializer_class = StockTransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['medicine', 'transaction_type', 'created_at']
    search_fields = ['medicine__name_en', 'medicine__name_ar', 'reference_number', 'notes']
    ordering_fields = ['created_at', 'quantity_change']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary"""
        queryset = self.get_queryset()
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        # Calculate summary
        summary = queryset.aggregate(
            total_transactions=Count('id'),
            total_in=Sum('quantity_change', filter=Q(transaction_type='in')),
            total_out=Sum('quantity_change', filter=Q(transaction_type='out')),
            total_adjustments=Sum('quantity_change', filter=Q(transaction_type='adjustment'))
        )
        
        return Response(summary)
