"""
API views for billing models.
"""

from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import (
    Patient, Doctor, ServiceCategory, Service, Invoice, InvoiceItem,
    PaymentMethod, Payment, Refund, Discount, AuditLog
)
from .serializers import (
    PatientSerializer, DoctorSerializer, ServiceCategorySerializer, ServiceSerializer,
    InvoiceSerializer, InvoiceCreateSerializer, InvoiceItemSerializer,
    PaymentMethodSerializer, PaymentSerializer, PaymentCreateSerializer,
    RefundSerializer, RefundCreateSerializer, DiscountSerializer, DiscountCreateSerializer,
    AuditLogSerializer, FinancialSummarySerializer, PaymentHistorySerializer
)
from .filters import InvoiceFilter, PaymentFilter, RefundFilter


class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet for managing patients."""
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient_id', 'first_name_en', 'first_name_ar', 'last_name_en', 'last_name_ar', 'phone']
    filterset_fields = ['date_of_birth']
    ordering_fields = ['created_at', 'last_name_en', 'first_name_en']
    ordering = ['last_name_en', 'first_name_en']

    @extend_schema(
        summary="Get patient payment history",
        description="Retrieve payment history for a specific patient",
        responses={200: PaymentHistorySerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def payment_history(self, request, pk=None):
        """Get payment history for a specific patient."""
        patient = self.get_object()
        invoices = Invoice.objects.filter(patient=patient).prefetch_related('payments', 'refunds')
        
        history_data = []
        for invoice in invoices:
            history_data.append({
                'invoice_number': invoice.invoice_number,
                'invoice_date': invoice.invoice_date,
                'total_amount': invoice.total_amount,
                'paid_amount': invoice.paid_amount,
                'outstanding_amount': invoice.outstanding_amount,
                'status': invoice.status,
                'payments': invoice.payments.all(),
                'refunds': invoice.refunds.all()
            })
        
        serializer = PaymentHistorySerializer(history_data, many=True)
        return Response(serializer.data)


class DoctorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing doctors."""
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['doctor_id', 'first_name_en', 'first_name_ar', 'last_name_en', 'last_name_ar', 'specialization_en']
    filterset_fields = ['specialization_en']
    ordering_fields = ['created_at', 'last_name_en', 'first_name_en']
    ordering = ['last_name_en', 'first_name_en']


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing service categories."""
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name_en', 'name_ar', 'description_en', 'description_ar']
    filterset_fields = ['is_active']
    ordering_fields = ['name_en', 'created_at']
    ordering = ['name_en']


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing services."""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['service_id', 'name_en', 'name_ar', 'description_en', 'description_ar']
    filterset_fields = ['category', 'service_type', 'is_active']
    ordering_fields = ['name_en', 'base_price', 'created_at']
    ordering = ['name_en']


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing invoices."""
    queryset = Invoice.objects.select_related('patient', 'doctor', 'created_by', 'updated_by').prefetch_related('items')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['invoice_number', 'patient__first_name_en', 'patient__last_name_en', 'doctor__first_name_en']
    filterset_class = InvoiceFilter
    ordering_fields = ['invoice_date', 'created', 'total_amount', 'outstanding_amount']
    ordering = ['-created', '-invoice_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        return InvoiceSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @extend_schema(
        summary="Calculate invoice totals",
        description="Recalculate totals for an invoice including tax and discount",
        responses={200: InvoiceSerializer}
    )
    @action(detail=True, methods=['post'])
    def calculate_totals(self, request, pk=None):
        """Recalculate totals for an invoice."""
        invoice = self.get_object()
        invoice.calculate_totals()
        invoice.save()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @extend_schema(
        summary="Mark invoice as paid",
        description="Mark an invoice as fully paid",
        responses={200: InvoiceSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark an invoice as fully paid."""
        invoice = self.get_object()
        invoice.paid_amount = invoice.total_amount
        invoice.save()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @extend_schema(
        summary="Cancel invoice",
        description="Cancel an invoice",
        responses={200: InvoiceSerializer}
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an invoice."""
        invoice = self.get_object()
        if invoice.status == Invoice.INVOICE_STATUS.paid:
            return Response(
                {'error': 'Cannot cancel a paid invoice'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        invoice.status = Invoice.INVOICE_STATUS.cancelled
        invoice.save()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @extend_schema(
        summary="Get overdue invoices",
        description="Get all overdue invoices",
        responses={200: InvoiceSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue invoices."""
        overdue_invoices = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status__in=[Invoice.INVOICE_STATUS.pending, Invoice.INVOICE_STATUS.draft]
        )
        serializer = self.get_serializer(overdue_invoices, many=True)
        return Response(serializer.data)


class InvoiceItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing invoice items."""
    queryset = InvoiceItem.objects.select_related('invoice', 'service')
    serializer_class = InvoiceItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['invoice__invoice_number', 'service__name_en', 'description_en']
    filterset_fields = ['service__category', 'service__service_type']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payment methods."""
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name_en', 'name_ar']
    filterset_fields = ['payment_type', 'is_active']
    ordering_fields = ['name_en', 'created_at']
    ordering = ['name_en']


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payments."""
    queryset = Payment.objects.select_related('invoice', 'payment_method', 'created_by', 'updated_by', 'verified_by')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['invoice__invoice_number', 'reference_number', 'notes_en']
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date', 'created', 'amount']
    ordering = ['-payment_date', '-created']

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @extend_schema(
        summary="Verify payment",
        description="Verify a payment",
        responses={200: PaymentSerializer}
    )
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a payment."""
        payment = self.get_object()
        payment.is_verified = True
        payment.verified_by = request.user
        payment.verified_at = timezone.now()
        payment.save()
        serializer = self.get_serializer(payment)
        return Response(serializer.data)

    @extend_schema(
        summary="Get payments by date range",
        description="Get payments within a specific date range",
        parameters=[
            OpenApiParameter('start_date', OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter('end_date', OpenApiTypes.DATE, description='End date'),
        ],
        responses={200: PaymentSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get payments by date range."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        if start_date:
            queryset = queryset.filter(payment_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__date__lte=end_date)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RefundViewSet(viewsets.ModelViewSet):
    """ViewSet for managing refunds."""
    queryset = Refund.objects.select_related('invoice', 'created_by', 'updated_by', 'processed_by')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['refund_number', 'invoice__invoice_number', 'reason_en', 'reason_ar']
    filterset_class = RefundFilter
    ordering_fields = ['created', 'processed_date', 'amount']
    ordering = ['-created']

    def get_serializer_class(self):
        if self.action == 'create':
            return RefundCreateSerializer
        return RefundSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @extend_schema(
        summary="Process refund",
        description="Process a refund",
        responses={200: RefundSerializer}
    )
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a refund."""
        refund = self.get_object()
        if refund.status != Refund.REFUND_STATUS.approved:
            return Response(
                {'error': 'Refund must be approved before processing'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        refund.status = Refund.REFUND_STATUS.processed
        refund.processed_by = request.user
        refund.processed_date = timezone.now()
        refund.save()
        serializer = self.get_serializer(refund)
        return Response(serializer.data)

    @extend_schema(
        summary="Approve refund",
        description="Approve a refund",
        responses={200: RefundSerializer}
    )
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a refund."""
        refund = self.get_object()
        if refund.status != Refund.REFUND_STATUS.pending:
            return Response(
                {'error': 'Refund must be pending to approve'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        refund.status = Refund.REFUND_STATUS.approved
        refund.save()
        serializer = self.get_serializer(refund)
        return Response(serializer.data)


class DiscountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing discounts."""
    queryset = Discount.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name_en', 'name_ar', 'code', 'description_en']
    filterset_fields = ['discount_type', 'is_active']
    ordering_fields = ['name_en', 'created_at', 'valid_from']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return DiscountCreateSerializer
        return DiscountSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(
        summary="Get valid discounts",
        description="Get all currently valid discounts",
        responses={200: DiscountSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def valid(self, request):
        """Get valid discounts."""
        valid_discounts = self.get_queryset().filter(is_active=True)
        now = timezone.now()
        valid_discounts = valid_discounts.filter(
            valid_from__lte=now,
            Q(valid_until__isnull=True) | Q(valid_until__gte=now)
        )
        serializer = self.get_serializer(valid_discounts, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Apply discount to invoice",
        description="Apply a discount to an invoice",
        parameters=[
            OpenApiParameter('invoice_id', OpenApiTypes.UUID, description='Invoice ID'),
        ],
        responses={200: InvoiceSerializer}
    )
    @action(detail=True, methods=['post'])
    def apply_to_invoice(self, request, pk=None):
        """Apply discount to an invoice."""
        discount = self.get_object()
        invoice_id = request.data.get('invoice_id')
        
        if not invoice_id:
            return Response(
                {'error': 'Invoice ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not discount.can_apply_to_invoice(invoice):
            return Response(
                {'error': 'Discount cannot be applied to this invoice'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        discount_amount = discount.calculate_discount_amount(invoice.subtotal)
        invoice.discount_amount = discount_amount
        invoice.calculate_totals()
        invoice.save()
        
        # Update usage count
        discount.used_count += 1
        discount.save()
        
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing audit logs."""
    queryset = AuditLog.objects.select_related('user', 'invoice', 'payment', 'refund', 'discount')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['action_type', 'description_en', 'description_ar', 'user__username']
    filterset_fields = ['action_type', 'user', 'timestamp']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


class FinancialReportsViewSet(viewsets.ViewSet):
    """ViewSet for financial reports."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get financial summary",
        description="Get financial summary for a specific period",
        parameters=[
            OpenApiParameter('start_date', OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter('end_date', OpenApiTypes.DATE, description='End date'),
        ],
        responses={200: FinancialSummarySerializer}
    )
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get financial summary."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date:
            start_date = (timezone.now() - timedelta(days=30)).date()
        if not end_date:
            end_date = timezone.now().date()
        
        # Convert to datetime for filtering
        start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
        
        invoices = Invoice.objects.filter(
            invoice_date__range=[start_datetime, end_datetime]
        )
        
        summary_data = {
            'total_invoices': invoices.count(),
            'total_revenue': invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'total_paid': invoices.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0,
            'total_outstanding': invoices.aggregate(Sum('outstanding_amount'))['outstanding_amount__sum'] or 0,
            'total_refunds': Refund.objects.filter(
                created__range=[start_datetime, end_datetime],
                status=Refund.REFUND_STATUS.processed
            ).aggregate(Sum('amount'))['amount__sum'] or 0,
            'total_discounts': invoices.aggregate(Sum('discount_amount'))['discount_amount__sum'] or 0,
            'period_start': start_datetime,
            'period_end': end_datetime
        }
        
        serializer = FinancialSummarySerializer(summary_data)
        return Response(serializer.data)

    @extend_schema(
        summary="Get revenue trends",
        description="Get revenue trends over time",
        parameters=[
            OpenApiParameter('period', OpenApiTypes.STR, description='Period: daily, weekly, monthly'),
            OpenApiParameter('start_date', OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter('end_date', OpenApiTypes.DATE, description='End date'),
        ],
        responses={200: serializers.Serializer}
    )
    @action(detail=False, methods=['get'])
    def revenue_trends(self, request):
        """Get revenue trends."""
        period = request.query_params.get('period', 'daily')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date:
            start_date = (timezone.now() - timedelta(days=30)).date()
        if not end_date:
            end_date = timezone.now().date()
        
        # Implementation for revenue trends would go here
        # This is a placeholder for the actual implementation
        return Response({'message': 'Revenue trends endpoint - implementation needed'})
