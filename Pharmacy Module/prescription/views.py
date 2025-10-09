from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Prescription, PrescriptionItem, DispensingRecord
from .serializers import (
    PrescriptionSerializer, PrescriptionCreateSerializer, PrescriptionListSerializer,
    PrescriptionItemSerializer, DispensingRecordSerializer, DispensingSerializer
)
from stock.models import Stock, StockTransaction


class PrescriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing prescriptions"""
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'prescription_date', 'patient_id', 'doctor_id']
    search_fields = [
        'prescription_number', 'patient_name', 'doctor_name', 
        'patient_id', 'doctor_id', 'consultation_id'
    ]
    ordering_fields = ['prescription_date', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PrescriptionCreateSerializer
        elif self.action == 'list':
            return PrescriptionListSerializer
        return PrescriptionSerializer

    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user"""
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending prescriptions"""
        queryset = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def partially_dispensed(self, request):
        """Get partially dispensed prescriptions"""
        queryset = self.get_queryset().filter(status='partially_dispensed')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a prescription"""
        prescription = self.get_object()
        if prescription.status == 'cancelled':
            return Response(
                {'error': 'Prescription is already cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prescription.status = 'cancelled'
        prescription.updated_by = request.user
        prescription.save()
        
        serializer = self.get_serializer(prescription)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def dispense_item(self, request, pk=None):
        """Dispense a specific item in the prescription"""
        prescription = self.get_object()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        if not item_id or not quantity:
            return Response(
                {'error': 'item_id and quantity are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = prescription.items.get(id=item_id)
        except PrescriptionItem.DoesNotExist:
            return Response(
                {'error': 'Item not found in this prescription'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if item.get_remaining_quantity() < quantity:
            return Response(
                {'error': f'Cannot dispense more than remaining quantity. Remaining: {item.get_remaining_quantity()}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update item
        item.dispensed_quantity += quantity
        item.updated_by = request.user
        item.save()
        
        # Update prescription status
        prescription.update_status()
        
        serializer = self.get_serializer(prescription)
        return Response(serializer.data)


class PrescriptionItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing prescription items"""
    queryset = PrescriptionItem.objects.all()
    serializer_class = PrescriptionItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['prescription', 'medicine']
    search_fields = ['medicine__name_en', 'medicine__name_ar']
    ordering_fields = ['medicine__name_en', 'quantity']
    ordering = ['medicine__name_en']

    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user"""
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def dispense(self, request, pk=None):
        """Dispense this prescription item"""
        item = self.get_object()
        serializer = DispensingSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity_to_dispense = serializer.validated_data['quantity_to_dispense']
            pharmacist_name = serializer.validated_data['pharmacist_name']
            pharmacist_id = serializer.validated_data.get('pharmacist_id', '')
            batch_number = serializer.validated_data.get('batch_number', '')
            notes_en = serializer.validated_data.get('notes_en', '')
            notes_ar = serializer.validated_data.get('notes_ar', '')
            
            # Find available stock (FIFO - First In, First Out)
            available_stock = Stock.objects.filter(
                medicine=item.medicine,
                is_active=True,
                quantity__gt=0
            ).order_by('expiration_date')
            
            if not available_stock.exists():
                return Response(
                    {'error': 'No stock available for this medicine'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Dispense from available stock
            remaining_to_dispense = quantity_to_dispense
            dispensing_records = []
            
            for stock in available_stock:
                if remaining_to_dispense <= 0:
                    break
                
                quantity_from_this_stock = min(remaining_to_dispense, stock.quantity)
                
                # Create dispensing record
                dispensing_record = DispensingRecord.objects.create(
                    prescription_item=item,
                    quantity_dispensed=quantity_from_this_stock,
                    pharmacist_name=pharmacist_name,
                    pharmacist_id=pharmacist_id,
                    stock_record=stock,
                    batch_number=batch_number or stock.batch_number,
                    notes_en=notes_en,
                    notes_ar=notes_ar,
                    created_by=request.user
                )
                dispensing_records.append(dispensing_record)
                
                # Record stock transaction
                StockTransaction.objects.create(
                    medicine=item.medicine,
                    stock_record=stock,
                    transaction_type='out',
                    quantity_change=-quantity_from_this_stock,
                    quantity_before=stock.quantity,
                    quantity_after=stock.quantity - quantity_from_this_stock,
                    reference_number=item.prescription.prescription_number,
                    reference_type='prescription',
                    notes=f'Dispensed for prescription {item.prescription.prescription_number}',
                    created_by=request.user
                )
                
                # Update stock quantity
                stock.quantity -= quantity_from_this_stock
                stock.updated_by = request.user
                stock.save()
                
                remaining_to_dispense -= quantity_from_this_stock
            
            if remaining_to_dispense > 0:
                return Response(
                    {'error': f'Insufficient stock. Could only dispense {quantity_to_dispense - remaining_to_dispense} out of {quantity_to_dispense} requested'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update prescription item
            item.dispensed_quantity += quantity_to_dispense
            item.updated_by = request.user
            item.save()
            
            # Update prescription status
            item.prescription.update_status()
            
            # Return dispensing records
            dispensing_serializer = DispensingRecordSerializer(dispensing_records, many=True)
            return Response({
                'message': f'Successfully dispensed {quantity_to_dispense} units',
                'dispensing_records': dispensing_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DispensingRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing dispensing records (read-only)"""
    queryset = DispensingRecord.objects.all()
    serializer_class = DispensingRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['prescription_item', 'pharmacist_id', 'dispensing_date']
    search_fields = [
        'medicine_name', 'medicine_name_ar', 'prescription_number', 
        'patient_name', 'pharmacist_name', 'batch_number'
    ]
    ordering_fields = ['dispensing_date', 'quantity_dispensed']
    ordering = ['-dispensing_date']

    @action(detail=False, methods=['get'])
    def by_pharmacist(self, request):
        """Get dispensing records by pharmacist"""
        pharmacist_id = request.query_params.get('pharmacist_id')
        if not pharmacist_id:
            return Response(
                {'error': 'pharmacist_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(pharmacist_id=pharmacist_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get dispensing records by date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date parameters are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            dispensing_date__date__gte=start_date,
            dispensing_date__date__lte=end_date
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
