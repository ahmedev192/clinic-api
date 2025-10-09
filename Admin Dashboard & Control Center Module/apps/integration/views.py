from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import (
    ModuleConnection, APICall, DataSync, SyncLog, 
    WebhookEndpoint, WebhookLog, IntegrationTest
)
from .serializers import (
    ModuleConnectionSerializer, APICallSerializer, DataSyncSerializer,
    SyncLogSerializer, WebhookEndpointSerializer, WebhookLogSerializer,
    IntegrationTestSerializer, IntegrationSummarySerializer, ConnectionStatusSerializer,
    TestResultSerializer
)
from .utils import (
    test_connection, make_api_call, run_data_sync, 
    process_webhook, run_integration_test, get_connection_status
)

logger = logging.getLogger('admin_dashboard')


class ModuleConnectionListCreateView(generics.ListCreateAPIView):
    """List and create module connections"""
    queryset = ModuleConnection.objects.all()
    serializer_class = ModuleConnectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        module_type = self.request.query_params.get('module_type')
        status_filter = self.request.query_params.get('status')
        is_enabled = self.request.query_params.get('is_enabled')
        
        if module_type:
            queryset = queryset.filter(module_type=module_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if is_enabled is not None:
            queryset = queryset.filter(is_enabled=is_enabled.lower() == 'true')
        
        return queryset.order_by('name')


class APICallListCreateView(generics.ListCreateAPIView):
    """List and create API calls"""
    queryset = APICall.objects.all()
    serializer_class = APICallSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        connection_id = self.request.query_params.get('connection_id')
        status_filter = self.request.query_params.get('status')
        method = self.request.query_params.get('method')
        days = int(self.request.query_params.get('days', 7))
        
        if connection_id:
            queryset = queryset.filter(connection_id=connection_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if method:
            queryset = queryset.filter(method=method)
        
        # Filter by date range
        since = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(timestamp__gte=since)
        
        return queryset.order_by('-timestamp')


class DataSyncListCreateView(generics.ListCreateAPIView):
    """List and create data syncs"""
    queryset = DataSync.objects.all()
    serializer_class = DataSyncSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        sync_type = self.request.query_params.get('sync_type')
        status_filter = self.request.query_params.get('status')
        is_enabled = self.request.query_params.get('is_enabled')
        
        if sync_type:
            queryset = queryset.filter(sync_type=sync_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if is_enabled is not None:
            queryset = queryset.filter(is_enabled=is_enabled.lower() == 'true')
        
        return queryset.order_by('name')


class SyncLogListCreateView(generics.ListCreateAPIView):
    """List and create sync logs"""
    queryset = SyncLog.objects.all()
    serializer_class = SyncLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        sync_id = self.request.query_params.get('sync_id')
        status_filter = self.request.query_params.get('status')
        days = int(self.request.query_params.get('days', 7))
        
        if sync_id:
            queryset = queryset.filter(sync_id=sync_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        since = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(started_at__gte=since)
        
        return queryset.order_by('-started_at')


class WebhookEndpointListCreateView(generics.ListCreateAPIView):
    """List and create webhook endpoints"""
    queryset = WebhookEndpoint.objects.all()
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        module_type = self.request.query_params.get('module_type')
        status_filter = self.request.query_params.get('status')
        is_enabled = self.request.query_params.get('is_enabled')
        
        if module_type:
            queryset = queryset.filter(module_type=module_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if is_enabled is not None:
            queryset = queryset.filter(is_enabled=is_enabled.lower() == 'true')
        
        return queryset.order_by('name')


class WebhookLogListCreateView(generics.ListCreateAPIView):
    """List and create webhook logs"""
    queryset = WebhookLog.objects.all()
    serializer_class = WebhookLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        endpoint_id = self.request.query_params.get('endpoint_id')
        status_filter = self.request.query_params.get('status')
        days = int(self.request.query_params.get('days', 7))
        
        if endpoint_id:
            queryset = queryset.filter(endpoint_id=endpoint_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        since = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(timestamp__gte=since)
        
        return queryset.order_by('-timestamp')


class IntegrationTestListCreateView(generics.ListCreateAPIView):
    """List and create integration tests"""
    queryset = IntegrationTest.objects.all()
    serializer_class = IntegrationTestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        connection_id = self.request.query_params.get('connection_id')
        test_type = self.request.query_params.get('test_type')
        status_filter = self.request.query_params.get('status')
        
        if connection_id:
            queryset = queryset.filter(connection_id=connection_id)
        if test_type:
            queryset = queryset.filter(test_type=test_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def integration_summary(request):
    """Get integration summary for dashboard"""
    try:
        # Get connection statistics
        total_connections = ModuleConnection.objects.count()
        active_connections = ModuleConnection.objects.filter(status='active').count()
        failed_connections = ModuleConnection.objects.filter(status='error').count()
        
        # Get API call statistics
        total_api_calls = APICall.objects.count()
        successful_api_calls = APICall.objects.filter(status='success').count()
        failed_api_calls = APICall.objects.filter(status='failed').count()
        
        # Get sync statistics
        total_syncs = DataSync.objects.count()
        active_syncs = DataSync.objects.filter(status='active').count()
        
        # Get webhook statistics
        total_webhooks = WebhookEndpoint.objects.count()
        active_webhooks = WebhookEndpoint.objects.filter(status='active').count()
        
        summary_data = {
            'total_connections': total_connections,
            'active_connections': active_connections,
            'failed_connections': failed_connections,
            'total_api_calls': total_api_calls,
            'successful_api_calls': successful_api_calls,
            'failed_api_calls': failed_api_calls,
            'total_syncs': total_syncs,
            'active_syncs': active_syncs,
            'total_webhooks': total_webhooks,
            'active_webhooks': active_webhooks,
            'last_updated': timezone.now()
        }
        
        serializer = IntegrationSummarySerializer(summary_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting integration summary: {str(e)}")
        return Response(
            {'error': f'Failed to get integration summary: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def connection_status(request):
    """Get status of all connections"""
    try:
        connections = ModuleConnection.objects.filter(is_enabled=True)
        status_data = []
        
        for connection in connections:
            status_info = get_connection_status(connection)
            status_data.append(status_info)
        
        serializer = ConnectionStatusSerializer(status_data, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting connection status: {str(e)}")
        return Response(
            {'error': f'Failed to get connection status: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_connection_api(request, connection_id):
    """Test a module connection"""
    try:
        try:
            connection = ModuleConnection.objects.get(id=connection_id)
        except ModuleConnection.DoesNotExist:
            return Response(
                {'error': 'Connection not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        result = test_connection(connection)
        
        if result['success']:
            connection.status = 'active'
            connection.last_checked = timezone.now()
            connection.last_error = None
        else:
            connection.status = 'error'
            connection.last_checked = timezone.now()
            connection.last_error = result['error']
        
        connection.save()
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        return Response(
            {'error': f'Failed to test connection: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_api_call_api(request):
    """Make an API call to a module"""
    try:
        connection_id = request.data.get('connection_id')
        endpoint = request.data.get('endpoint')
        method = request.data.get('method', 'GET')
        data = request.data.get('data', {})
        
        if not all([connection_id, endpoint]):
            return Response(
                {'error': 'Connection ID and endpoint are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            connection = ModuleConnection.objects.get(id=connection_id)
        except ModuleConnection.DoesNotExist:
            return Response(
                {'error': 'Connection not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        result = make_api_call(connection, endpoint, method, data, request.user)
        
        serializer = APICallSerializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error making API call: {str(e)}")
        return Response(
            {'error': f'Failed to make API call: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_sync_api(request, sync_id):
    """Run a data sync"""
    try:
        try:
            sync = DataSync.objects.get(id=sync_id)
        except DataSync.DoesNotExist:
            return Response(
                {'error': 'Sync not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        result = run_data_sync(sync)
        
        serializer = SyncLogSerializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error running sync: {str(e)}")
        return Response(
            {'error': f'Failed to run sync: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_integration_test_api(request, test_id):
    """Run an integration test"""
    try:
        try:
            test = IntegrationTest.objects.get(id=test_id)
        except IntegrationTest.DoesNotExist:
            return Response(
                {'error': 'Test not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        result = run_integration_test(test, request.user)
        
        serializer = IntegrationTestSerializer(result)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error running integration test: {str(e)}")
        return Response(
            {'error': f'Failed to run integration test: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_all_tests(request):
    """Run all integration tests"""
    try:
        connection_id = request.data.get('connection_id')
        
        if connection_id:
            tests = IntegrationTest.objects.filter(connection_id=connection_id)
        else:
            tests = IntegrationTest.objects.all()
        
        results = []
        for test in tests:
            result = run_integration_test(test, request.user)
            results.append({
                'test_id': test.id,
                'test_name': test.name,
                'status': result.status,
                'error_message': result.error_message
            })
        
        return Response(results)
        
    except Exception as e:
        logger.error(f"Error running all tests: {str(e)}")
        return Response(
            {'error': f'Failed to run all tests: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def webhook_receiver(request, endpoint_path):
    """Receive webhook data from other modules"""
    try:
        try:
            endpoint = WebhookEndpoint.objects.get(
                endpoint_path=endpoint_path,
                is_enabled=True
            )
        except WebhookEndpoint.DoesNotExist:
            return Response(
                {'error': 'Webhook endpoint not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        result = process_webhook(endpoint, request)
        
        if result['success']:
            return Response({'status': 'success'})
        else:
            return Response(
                {'error': result['error']}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return Response(
            {'error': f'Failed to process webhook: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
