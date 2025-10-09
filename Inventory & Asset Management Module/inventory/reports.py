"""
Inventory reporting functionality
"""
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum, Count, F, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Item, StockMovement, PurchaseOrder, MaintenanceRecord, Alert
from .utils import generate_inventory_report, get_dashboard_data


class ReportMixin:
    """Mixin for report functionality"""
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard data"""
        data = get_dashboard_data()
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def stock_levels(self, request):
        """Get stock levels report"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Group by item type
        by_type = queryset.values('item_type').annotate(
            count=Count('id'),
            total_quantity=Sum('current_quantity'),
            total_value=Sum(F('current_quantity') * F('unit_cost'))
        )
        
        # Group by category
        by_category = queryset.values('category__name_en', 'category__name_ar').annotate(
            count=Count('id'),
            total_quantity=Sum('current_quantity'),
            total_value=Sum(F('current_quantity') * F('unit_cost'))
        )
        
        # Low stock items
        low_stock = queryset.filter(
            current_quantity__lte=F('reorder_level'),
            status='active'
        ).values('id', 'code', 'name_en', 'name_ar', 'current_quantity', 'reorder_level')
        
        # Expired items
        today = timezone.now().date()
        expired = queryset.filter(
            expiry_date__lt=today,
            status='active'
        ).values('id', 'code', 'name_en', 'name_ar', 'expiry_date')
        
        # Expiring soon (within 30 days)
        future_date = today + timedelta(days=30)
        expiring_soon = queryset.filter(
            expiry_date__gte=today,
            expiry_date__lte=future_date,
            status='active'
        ).values('id', 'code', 'name_en', 'name_ar', 'expiry_date')
        
        return Response({
            'by_type': by_type,
            'by_category': by_category,
            'low_stock_items': low_stock,
            'expired_items': expired,
            'expiring_soon': expiring_soon
        })
    
    @action(detail=False, methods=['get'])
    def stock_movements(self, request):
        """Get stock movements report"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Date range filter
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created__date__lte=end_date)
        
        # Group by movement type
        by_type = queryset.values('movement_type').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity')
        )
        
        # Group by item
        by_item = queryset.values(
            'item__code', 'item__name_en', 'item__name_ar'
        ).annotate(
            count=Count('id'),
            total_in=Sum('quantity', filter=Q(movement_type='in')),
            total_out=Sum('quantity', filter=Q(movement_type='out')),
            net_movement=Sum(
                F('quantity') * F('movement_type'),
                output_field=models.IntegerField()
            )
        )
        
        # Group by department
        by_department = queryset.values('department').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity')
        ).exclude(department='')
        
        # Daily movements
        daily_movements = queryset.extra(
            select={'day': 'date(created)'}
        ).values('day').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity')
        ).order_by('day')
        
        return Response({
            'by_type': by_type,
            'by_item': by_item,
            'by_department': by_department,
            'daily_movements': daily_movements
        })
    
    @action(detail=False, methods=['get'])
    def purchase_orders(self, request):
        """Get purchase orders report"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Date range filter
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(order_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__date__lte=end_date)
        
        # Group by status
        by_status = queryset.values('status').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount'),
            avg_amount=Avg('total_amount')
        )
        
        # Group by supplier
        by_supplier = queryset.values(
            'supplier__name_en', 'supplier__name_ar'
        ).annotate(
            count=Count('id'),
            total_amount=Sum('total_amount'),
            avg_amount=Avg('total_amount')
        )
        
        # Monthly orders
        monthly_orders = queryset.extra(
            select={'month': 'strftime("%Y-%m", order_date)'}
        ).values('month').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        ).order_by('month')
        
        # Pending orders
        pending_orders = queryset.filter(
            status__in=['draft', 'ordered', 'partial']
        ).values(
            'id', 'order_number', 'supplier__name_en', 'status',
            'order_date', 'expected_delivery', 'total_amount'
        )
        
        return Response({
            'by_status': by_status,
            'by_supplier': by_supplier,
            'monthly_orders': monthly_orders,
            'pending_orders': pending_orders
        })
    
    @action(detail=False, methods=['get'])
    def maintenance(self, request):
        """Get maintenance report"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Date range filter
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(scheduled_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(scheduled_date__date__lte=end_date)
        
        # Group by maintenance type
        by_type = queryset.values('maintenance_type').annotate(
            count=Count('id'),
            total_cost=Sum('cost'),
            avg_cost=Avg('cost')
        )
        
        # Group by status
        by_status = queryset.values('status').annotate(
            count=Count('id')
        )
        
        # Group by item
        by_item = queryset.values(
            'item__code', 'item__name_en', 'item__name_ar'
        ).annotate(
            count=Count('id'),
            total_cost=Sum('cost'),
            last_maintenance=Max('completed_date')
        )
        
        # Due maintenance
        today = timezone.now().date()
        due_maintenance = queryset.filter(
            next_maintenance_date__lte=today,
            status__in=['scheduled', 'in_progress']
        ).values(
            'id', 'item__code', 'item__name_en', 'item__name_ar',
            'next_maintenance_date', 'maintenance_type'
        )
        
        # Overdue maintenance
        overdue_maintenance = queryset.filter(
            next_maintenance_date__lt=today,
            status__in=['scheduled', 'in_progress']
        ).values(
            'id', 'item__code', 'item__name_en', 'item__name_ar',
            'next_maintenance_date', 'maintenance_type'
        )
        
        return Response({
            'by_type': by_type,
            'by_status': by_status,
            'by_item': by_item,
            'due_maintenance': due_maintenance,
            'overdue_maintenance': overdue_maintenance
        })
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """Get alerts report"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Group by alert type
        by_type = queryset.values('alert_type').annotate(
            count=Count('id'),
            unread=Count('id', filter=Q(is_read=False)),
            unresolved=Count('id', filter=Q(is_resolved=False))
        )
        
        # Group by priority
        by_priority = queryset.values('priority').annotate(
            count=Count('id'),
            unread=Count('id', filter=Q(is_read=False)),
            unresolved=Count('id', filter=Q(is_resolved=False))
        )
        
        # Recent alerts
        recent_alerts = queryset.order_by('-created')[:20].values(
            'id', 'alert_type', 'priority', 'title_en', 'title_ar',
            'is_read', 'is_resolved', 'created'
        )
        
        # Critical alerts
        critical_alerts = queryset.filter(
            priority='critical',
            is_resolved=False
        ).values(
            'id', 'alert_type', 'title_en', 'title_ar', 'created'
        )
        
        return Response({
            'by_type': by_type,
            'by_priority': by_priority,
            'recent_alerts': recent_alerts,
            'critical_alerts': critical_alerts
        })
    
    @action(detail=False, methods=['get'])
    def comprehensive(self, request):
        """Get comprehensive inventory report"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = timezone.now().date() - timedelta(days=30)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()
        
        report = generate_inventory_report(start_date, end_date)
        return Response(report)
