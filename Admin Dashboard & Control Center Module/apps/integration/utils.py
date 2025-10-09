"""
Utility functions for integration app
"""
import requests
import json
import time
import logging
from django.utils import timezone
from django.conf import settings
from .models import (
    ModuleConnection, APICall, DataSync, SyncLog, 
    WebhookEndpoint, WebhookLog, IntegrationTest
)

logger = logging.getLogger('admin_dashboard')


def test_connection(connection):
    """Test a module connection"""
    try:
        start_time = time.time()
        
        # Make a simple health check request
        url = f"{connection.base_url.rstrip('/')}/health/"
        headers = get_auth_headers(connection)
        
        response = requests.get(url, headers=headers, timeout=connection.timeout)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            # Update connection status
            connection.status = 'active'
            connection.last_checked = timezone.now()
            connection.last_error = None
            connection.save()
            
            return {
                'success': True,
                'response_time': response_time,
                'status_code': response.status_code,
                'message': 'Connection successful'
            }
        else:
            # Update connection status
            connection.status = 'error'
            connection.last_checked = timezone.now()
            connection.last_error = f'HTTP {response.status_code}: {response.text}'
            connection.save()
            
            return {
                'success': False,
                'response_time': response_time,
                'status_code': response.status_code,
                'error': f'HTTP {response.status_code}: {response.text}'
            }
            
    except requests.exceptions.Timeout:
        connection.status = 'error'
        connection.last_checked = timezone.now()
        connection.last_error = 'Request timeout'
        connection.save()
        
        return {
            'success': False,
            'error': 'Request timeout'
        }
    except requests.exceptions.RequestException as e:
        connection.status = 'error'
        connection.last_checked = timezone.now()
        connection.last_error = str(e)
        connection.save()
        
        return {
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Error testing connection {connection.name}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def make_api_call(connection, endpoint, method='GET', data=None, user=None):
    """Make an API call to a module"""
    try:
        start_time = time.time()
        
        # Create API call record
        api_call = APICall.objects.create(
            connection=connection,
            endpoint=endpoint,
            method=method,
            request_data=data or {},
            initiated_by=user,
            status='pending'
        )
        
        # Prepare request
        url = f"{connection.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = get_auth_headers(connection)
        headers['Content-Type'] = 'application/json'
        
        # Make the request
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=connection.timeout)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=connection.timeout)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=connection.timeout)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=connection.timeout)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=connection.timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response_time = time.time() - start_time
        
        # Update API call record
        api_call.status = 'success' if response.status_code < 400 else 'failed'
        api_call.status_code = response.status_code
        api_call.response_time = response_time
        
        try:
            api_call.response_data = response.json()
        except:
            api_call.response_data = {'text': response.text}
        
        if response.status_code >= 400:
            api_call.error_message = f'HTTP {response.status_code}: {response.text}'
        
        api_call.save()
        
        return api_call
        
    except requests.exceptions.Timeout:
        api_call.status = 'timeout'
        api_call.error_message = 'Request timeout'
        api_call.save()
        return api_call
    except requests.exceptions.RequestException as e:
        api_call.status = 'failed'
        api_call.error_message = str(e)
        api_call.save()
        return api_call
    except Exception as e:
        logger.error(f"Error making API call: {str(e)}")
        api_call.status = 'failed'
        api_call.error_message = str(e)
        api_call.save()
        return api_call


def get_auth_headers(connection):
    """Get authentication headers for a connection"""
    headers = {}
    
    if connection.authentication_type == 'api_key':
        api_key = connection.auth_config.get('api_key')
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
    elif connection.authentication_type == 'token':
        token = connection.auth_config.get('token')
        if token:
            headers['Authorization'] = f'Token {token}'
    elif connection.authentication_type == 'basic':
        username = connection.auth_config.get('username')
        password = connection.auth_config.get('password')
        if username and password:
            import base64
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers['Authorization'] = f'Basic {credentials}'
    elif connection.authentication_type == 'oauth':
        access_token = connection.auth_config.get('access_token')
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
    
    return headers


def run_data_sync(sync):
    """Run a data synchronization"""
    try:
        # Create sync log
        sync_log = SyncLog.objects.create(
            sync=sync,
            status='started'
        )
        
        # Get data from source
        source_connection = sync.source_module
        source_data = make_api_call(
            source_connection, 
            sync.source_endpoint, 
            'GET'
        )
        
        if source_data.status != 'success':
            sync_log.status = 'failed'
            sync_log.error_message = f'Failed to get data from source: {source_data.error_message}'
            sync_log.completed_at = timezone.now()
            sync_log.save()
            return sync_log
        
        # Process and transform data
        processed_data = transform_data(
            source_data.response_data, 
            sync.mapping_config
        )
        
        # Send data to target
        target_connection = sync.target_module
        target_response = make_api_call(
            target_connection,
            sync.target_endpoint,
            'POST',
            processed_data
        )
        
        # Update sync log
        if target_response.status == 'success':
            sync_log.status = 'completed'
            sync_log.records_processed = len(processed_data.get('data', []))
            sync_log.records_successful = sync_log.records_processed
        else:
            sync_log.status = 'failed'
            sync_log.error_message = f'Failed to send data to target: {target_response.error_message}'
            sync_log.records_failed = sync_log.records_processed
        
        sync_log.completed_at = timezone.now()
        sync_log.duration = (sync_log.completed_at - sync_log.started_at).total_seconds()
        sync_log.save()
        
        # Update sync statistics
        sync.sync_count += 1
        if sync_log.status == 'failed':
            sync.error_count += 1
        sync.last_sync = sync_log.started_at
        sync.save()
        
        return sync_log
        
    except Exception as e:
        logger.error(f"Error running data sync: {str(e)}")
        sync_log.status = 'failed'
        sync_log.error_message = str(e)
        sync_log.completed_at = timezone.now()
        sync_log.save()
        return sync_log


def transform_data(data, mapping_config):
    """Transform data according to mapping configuration"""
    try:
        # This is a simplified transformation
        # In a real implementation, this would handle complex field mappings
        transformed_data = {
            'data': data.get('data', []),
            'metadata': {
                'transformed_at': timezone.now().isoformat(),
                'mapping_config': mapping_config
            }
        }
        
        return transformed_data
        
    except Exception as e:
        logger.error(f"Error transforming data: {str(e)}")
        return data


def process_webhook(endpoint, request):
    """Process incoming webhook data"""
    try:
        # Create webhook log
        webhook_log = WebhookLog.objects.create(
            endpoint=endpoint,
            status='received',
            payload=request.data,
            headers=dict(request.headers),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        # Validate webhook signature if secret key is configured
        if endpoint.secret_key:
            if not validate_webhook_signature(request, endpoint.secret_key):
                webhook_log.status = 'failed'
                webhook_log.error_message = 'Invalid webhook signature'
                webhook_log.save()
                return {'success': False, 'error': 'Invalid webhook signature'}
        
        # Process webhook data
        start_time = time.time()
        
        # Call the handler function
        handler_result = call_webhook_handler(endpoint.handler_function, request.data)
        
        processing_time = time.time() - start_time
        
        # Update webhook log
        if handler_result['success']:
            webhook_log.status = 'processed'
            webhook_log.response_data = handler_result.get('response', {})
        else:
            webhook_log.status = 'failed'
            webhook_log.error_message = handler_result.get('error', 'Unknown error')
        
        webhook_log.processing_time = processing_time
        webhook_log.save()
        
        return handler_result
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {'success': False, 'error': str(e)}


def validate_webhook_signature(request, secret_key):
    """Validate webhook signature"""
    try:
        # This is a simplified validation
        # In a real implementation, this would validate HMAC signatures
        signature = request.headers.get('X-Webhook-Signature')
        if not signature:
            return False
        
        # For now, just check if signature exists
        return bool(signature)
        
    except Exception as e:
        logger.error(f"Error validating webhook signature: {str(e)}")
        return False


def call_webhook_handler(handler_function, data):
    """Call the webhook handler function"""
    try:
        # This would dynamically call the handler function
        # For now, return a mock response
        return {
            'success': True,
            'response': {'message': 'Webhook processed successfully'},
            'data': data
        }
        
    except Exception as e:
        logger.error(f"Error calling webhook handler: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def run_integration_test(test, user):
    """Run an integration test"""
    try:
        # Update test status
        test.status = 'running'
        test.run_by = user
        test.started_at = timezone.now()
        test.save()
        
        start_time = time.time()
        
        # Run the test based on type
        if test.test_type == 'connectivity':
            result = test_connectivity(test)
        elif test.test_type == 'authentication':
            result = test_authentication(test)
        elif test.test_type == 'data_retrieval':
            result = test_data_retrieval(test)
        elif test.test_type == 'data_submission':
            result = test_data_submission(test)
        elif test.test_type == 'full_integration':
            result = test_full_integration(test)
        else:
            result = {'success': False, 'error': 'Unknown test type'}
        
        duration = time.time() - start_time
        
        # Update test results
        test.status = 'passed' if result['success'] else 'failed'
        test.actual_result = result
        test.error_message = result.get('error')
        test.completed_at = timezone.now()
        test.duration = duration
        test.save()
        
        return test
        
    except Exception as e:
        logger.error(f"Error running integration test: {str(e)}")
        test.status = 'failed'
        test.error_message = str(e)
        test.completed_at = timezone.now()
        test.save()
        return test


def test_connectivity(test):
    """Test module connectivity"""
    try:
        result = test_connection(test.connection)
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}


def test_authentication(test):
    """Test module authentication"""
    try:
        # Test authentication by making a simple API call
        api_call = make_api_call(test.connection, 'auth/test/', 'GET')
        return {
            'success': api_call.status == 'success',
            'status_code': api_call.status_code,
            'error': api_call.error_message
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def test_data_retrieval(test):
    """Test data retrieval from module"""
    try:
        endpoint = test.test_config.get('endpoint', 'data/')
        api_call = make_api_call(test.connection, endpoint, 'GET')
        return {
            'success': api_call.status == 'success',
            'data_count': len(api_call.response_data.get('data', [])),
            'error': api_call.error_message
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def test_data_submission(test):
    """Test data submission to module"""
    try:
        endpoint = test.test_config.get('endpoint', 'data/')
        test_data = test.test_config.get('test_data', {})
        api_call = make_api_call(test.connection, endpoint, 'POST', test_data)
        return {
            'success': api_call.status == 'success',
            'status_code': api_call.status_code,
            'error': api_call.error_message
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def test_full_integration(test):
    """Test full integration workflow"""
    try:
        # Test connectivity
        connectivity_result = test_connectivity(test)
        if not connectivity_result['success']:
            return connectivity_result
        
        # Test authentication
        auth_result = test_authentication(test)
        if not auth_result['success']:
            return auth_result
        
        # Test data retrieval
        retrieval_result = test_data_retrieval(test)
        if not retrieval_result['success']:
            return retrieval_result
        
        # Test data submission
        submission_result = test_data_submission(test)
        if not submission_result['success']:
            return submission_result
        
        return {
            'success': True,
            'message': 'Full integration test passed',
            'details': {
                'connectivity': connectivity_result,
                'authentication': auth_result,
                'data_retrieval': retrieval_result,
                'data_submission': submission_result
            }
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_connection_status(connection):
    """Get detailed status of a connection"""
    try:
        # Test the connection
        result = test_connection(connection)
        
        return {
            'connection_name': connection.name,
            'module_type': connection.module_type,
            'status': connection.status,
            'last_checked': connection.last_checked,
            'response_time': result.get('response_time'),
            'error_message': connection.last_error
        }
        
    except Exception as e:
        logger.error(f"Error getting connection status: {str(e)}")
        return {
            'connection_name': connection.name,
            'module_type': connection.module_type,
            'status': 'error',
            'last_checked': None,
            'response_time': None,
            'error_message': str(e)
        }


def schedule_syncs():
    """Schedule pending data syncs"""
    try:
        from datetime import timedelta
        
        # Get scheduled syncs that are due
        now = timezone.now()
        due_syncs = DataSync.objects.filter(
            is_enabled=True,
            status='active',
            next_sync__lte=now
        )
        
        for sync in due_syncs:
            try:
                # Run the sync
                run_data_sync(sync)
                
                # Calculate next sync time
                if sync.sync_type == 'scheduled':
                    schedule_config = sync.schedule_config
                    interval_hours = schedule_config.get('interval_hours', 24)
                    sync.next_sync = now + timedelta(hours=interval_hours)
                    sync.save()
                
            except Exception as e:
                logger.error(f"Error running scheduled sync {sync.name}: {str(e)}")
        
        logger.info(f"Processed {due_syncs.count()} scheduled syncs")
        
    except Exception as e:
        logger.error(f"Error scheduling syncs: {str(e)}")


def cleanup_old_logs(days=30):
    """Clean up old integration logs"""
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Clean up old API calls
        api_calls_deleted = APICall.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        # Clean up old sync logs
        sync_logs_deleted = SyncLog.objects.filter(
            started_at__lt=cutoff_date
        ).delete()[0]
        
        # Clean up old webhook logs
        webhook_logs_deleted = WebhookLog.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {api_calls_deleted} API calls, {sync_logs_deleted} sync logs, "
                   f"{webhook_logs_deleted} webhook logs")
        
        return {
            'api_calls_deleted': api_calls_deleted,
            'sync_logs_deleted': sync_logs_deleted,
            'webhook_logs_deleted': webhook_logs_deleted,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old logs: {str(e)}")
        return {'error': str(e)}
