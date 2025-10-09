from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Category, Medicine
from .serializers import CategorySerializer, MedicineSerializer, MedicineListSerializer, MedicineSearchSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing medicine categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name_en', 'name_ar', 'description_en', 'description_ar']
    ordering_fields = ['name_en', 'name_ar', 'created_at']
    ordering = ['name_en']

    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user"""
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active categories"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MedicineViewSet(viewsets.ModelViewSet):
    """ViewSet for managing medicines"""
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'dosage_form', 'is_active', 'is_archived']
    search_fields = [
        'name_en', 'name_ar', 'generic_name_en', 'generic_name_ar',
        'brand_name_en', 'brand_name_ar', 'internal_code'
    ]
    ordering_fields = ['name_en', 'name_ar', 'created_at', 'reorder_level']
    ordering = ['name_en']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return MedicineListSerializer
        elif self.action == 'search':
            return MedicineSearchSerializer
        return MedicineSerializer

    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user"""
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search medicines by name, generic name, or brand name"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(
            Q(name_en__icontains=query) |
            Q(name_ar__icontains=query) |
            Q(generic_name_en__icontains=query) |
            Q(generic_name_ar__icontains=query) |
            Q(brand_name_en__icontains=query) |
            Q(brand_name_ar__icontains=query) |
            Q(internal_code__icontains=query)
        ).filter(is_active=True, is_archived=False)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get medicines with low stock"""
        queryset = self.get_queryset().filter(is_active=True, is_archived=False)
        low_stock_medicines = [medicine for medicine in queryset if medicine.is_low_stock()]
        serializer = self.get_serializer(low_stock_medicines, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get medicines with stock expiring soon"""
        days = int(request.query_params.get('days', 30))
        queryset = self.get_queryset().filter(is_active=True, is_archived=False)
        expiring_medicines = []
        
        for medicine in queryset:
            expiring_stock = medicine.get_expiring_soon(days)
            if expiring_stock.exists():
                expiring_medicines.append(medicine)
        
        serializer = self.get_serializer(expiring_medicines, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get medicines with expired stock"""
        queryset = self.get_queryset().filter(is_active=True, is_archived=False)
        expired_medicines = []
        
        for medicine in queryset:
            expired_stock = medicine.get_expired()
            if expired_stock.exists():
                expired_medicines.append(medicine)
        
        serializer = self.get_serializer(expired_medicines, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a medicine"""
        medicine = self.get_object()
        medicine.is_archived = True
        medicine.updated_by = request.user
        medicine.save()
        serializer = self.get_serializer(medicine)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        """Unarchive a medicine"""
        medicine = self.get_object()
        medicine.is_archived = False
        medicine.updated_by = request.user
        medicine.save()
        serializer = self.get_serializer(medicine)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a medicine"""
        medicine = self.get_object()
        medicine.is_active = False
        medicine.updated_by = request.user
        medicine.save()
        serializer = self.get_serializer(medicine)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a medicine"""
        medicine = self.get_object()
        medicine.is_active = True
        medicine.updated_by = request.user
        medicine.save()
        serializer = self.get_serializer(medicine)
        return Response(serializer.data)
