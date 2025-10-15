"""
Utility functions for monitoring app
"""
import requests
import psutil
import time
import logging
from django.conf import settings
from django.utils import timezone
from django.db import connection
from .models import SystemHealth, ModuleConnectivity, SystemAlert, PerformanceMetric

logger = logging.getLogger('admin_dashboard')


def check_system_health():
    """Check overall system health"""
    health_checks = []
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_checks.append({
            'component': 'database',
            'status': 'healthy',
            'message': 'Database connection successful',
            'response_time': 0.1
        })
    except Exception as e:
        health_checks.append({
            'component': 'database',
            'status': 'critical',
            'message': f'Database connection failed: {str(e)}',
            'response_time': None
        })
    
    # Check Redis connectivity
    try:
        import redis
        r = redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        health_checks.append({
            'component': 'redis',
            'status': 'healthy',
            'message': 'Redis connection successful',
            'response_time': 0.05
        })
    except Exception as e:
        health_checks.append({
            'component': 'redis',
            'status': 'warning',
            'message': f'Redis connection failed: {str(e)}',
            'response_time': None
        })
    
    # Check disk space
    try:
        disk_usage = psutil.disk_usage('/')
        free_percent = (disk_usage.free / disk_usage.total) * 100
        
        if free_percent < 10:
            status = 'critical'
            message = f'Disk space critically low: {free_percent:.1f}% free'
        elif free_percent < 20:
            status = 'warning'
            message = f'Disk space low: {free_percent:.1f}% free'
        else:
            status = 'healthy'
            message = f'Disk space OK: {free_percent:.1f}% free'
        
        health_checks.append({
            'component': 'disk_space',
            'status': status,
            'message': message,
            'response_time': 0.01
        })
    except Exception as e:
        health_checks.append({
            'component': 'disk_space',
            'status': 'unknown',
            'message': f'Could not check disk space: {str(e)}',
            'response_time': None
        })
    
    # Check memory usage
    try:
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        if memory_percent > 90:
            status = 'critical'
            message = f'Memory usage critically high: {memory_percent:.1f}%'
        elif memory_percent > 80:
            status = 'warning'
            message = f'Memory usage high: {memory_percent:.1f}%'
        else:
            status = 'healthy'
            message = f'Memory usage OK: {memory_percent:.1f}%'
        
        health_checks.append({
            'component': 'memory',
            'status': status,
            'message': message,
            'response_time': 0.01
        })
    except Exception as e:
        health_checks.append({
            'component': 'memory',
            'status': 'unknown',
            'message': f'Could not check memory usage: {str(e)}',
            'response_time': None
        })
    
    # Update SystemHealth records
    for check in health_checks:
        SystemHealth.objects.update_or_create(
            component=check['component'],
            defaults={
                'status': check['status'],
                'message': check['message'],
                'response_time': check['response_time'],
                'metadata': {'checked_at': timezone.now().isoformat()}
            }
        )
    
    return health_checks


def check_module_connectivity():
    """Check connectivity to all modules"""
    connectivity_checks = []
    
    for module_name, base_url in settings.MODULE_URLS.items():
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}health/", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                status = 'connected'
                error_message = None
            else:
                status = 'error'
                error_message = f'HTTP {response.status_code}'
            
            connectivity_checks.append({
                'module_name': module_name,
                'base_url': base_url,
                'status': status,
                'response_time': response_time,
                'error_message': error_message
            })
            
        except requests.exceptions.Timeout:
            connectivity_checks.append({
                'module_name': module_name,
                'base_url': base_url,
                'status': 'timeout',
                'response_time': None,
                'error_message': 'Request timeout'
            })
        except requests.exceptions.RequestException as e:
            connectivity_checks.append({
                'module_name': module_name,
                'base_url': base_url,
                'status': 'disconnected',
                'response_time': None,
                'error_message': str(e)
            })
    
    # Update ModuleConnectivity records
    for check in connectivity_checks:
        ModuleConnectivity.objects.update_or_create(
            module_name=check['module_name'],
            defaults={
                'base_url': check['base_url'],
                'status': check['status'],
                'response_time': check['response_time'],
                'error_message': check['error_message']
            }
        )
    
    return connectivity_checks


def run_health_checks(health_checks):
    """Run specific health checks"""
    results = []
    
    for health_check in health_checks:
        try:
            if health_check.check_type == 'http':
                result = _check_http_endpoint(health_check)
            elif health_check.check_type == 'database':
                result = _check_database(health_check)
            elif health_check.check_type == 'redis':
                result = _check_redis(health_check)
            elif health_check.check_type == 'disk_space':
                result = _check_disk_space(health_check)
            elif health_check.check_type == 'memory':
                result = _check_memory(health_check)
            else:
                result = {
                    'check_name': health_check.name,
                    'status': 'unknown',
                    'response_time': None,
                    'message': 'Unknown check type',
                    'timestamp': timezone.now()
                }
            
            # Update health check record
            health_check.last_run = timezone.now()
            health_check.last_status = result['status']
            health_check.last_message = result['message']
            health_check.save()
            
            results.append(result)
            
        except Exception as e:
            logger.error(f"Error running health check {health_check.name}: {str(e)}")
            result = {
                'check_name': health_check.name,
                'status': 'error',
                'response_time': None,
                'message': f'Health check failed: {str(e)}',
                'timestamp': timezone.now()
            }
            results.append(result)
    
    return results


def _check_http_endpoint(health_check):
    """Check HTTP endpoint"""
    try:
        start_time = time.time()
        response = requests.get(health_check.endpoint, timeout=health_check.timeout)
        response_time = time.time() - start_time
        
        if response.status_code == health_check.expected_status:
            status = 'healthy'
            message = f'HTTP {response.status_code} - OK'
        else:
            status = 'warning'
            message = f'HTTP {response.status_code} - Expected {health_check.expected_status}'
        
        return {
            'check_name': health_check.name,
            'status': status,
            'response_time': response_time,
            'message': message,
            'timestamp': timezone.now()
        }
        
    except requests.exceptions.Timeout:
        return {
            'check_name': health_check.name,
            'status': 'critical',
            'response_time': None,
            'message': 'Request timeout',
            'timestamp': timezone.now()
        }
    except Exception as e:
        return {
            'check_name': health_check.name,
            'status': 'critical',
            'response_time': None,
            'message': f'Request failed: {str(e)}',
            'timestamp': timezone.now()
        }


def _check_database(health_check):
    """Check database connectivity"""
    try:
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        response_time = time.time() - start_time
        
        return {
            'check_name': health_check.name,
            'status': 'healthy',
            'response_time': response_time,
            'message': 'Database connection successful',
            'timestamp': timezone.now()
        }
        
    except Exception as e:
        return {
            'check_name': health_check.name,
            'status': 'critical',
            'response_time': None,
            'message': f'Database connection failed: {str(e)}',
            'timestamp': timezone.now()
        }


def _check_redis(health_check):
    """Check Redis connectivity"""
    try:
        start_time = time.time()
        import redis
        r = redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        response_time = time.time() - start_time
        
        return {
            'check_name': health_check.name,
            'status': 'healthy',
            'response_time': response_time,
            'message': 'Redis connection successful',
            'timestamp': timezone.now()
        }
        
    except Exception as e:
        return {
            'check_name': health_check.name,
            'status': 'warning',
            'response_time': None,
            'message': f'Redis connection failed: {str(e)}',
            'timestamp': timezone.now()
        }


def _check_disk_space(health_check):
    """Check disk space"""
    try:
        disk_usage = psutil.disk_usage('/')
        free_percent = (disk_usage.free / disk_usage.total) * 100
        
        if free_percent < 10:
            status = 'critical'
            message = f'Disk space critically low: {free_percent:.1f}% free'
        elif free_percent < 20:
            status = 'warning'
            message = f'Disk space low: {free_percent:.1f}% free'
        else:
            status = 'healthy'
            message = f'Disk space OK: {free_percent:.1f}% free'
        
        return {
            'check_name': health_check.name,
            'status': status,
            'response_time': 0.01,
            'message': message,
            'timestamp': timezone.now()
        }
        
    except Exception as e:
        return {
            'check_name': health_check.name,
            'status': 'unknown',
            'response_time': None,
            'message': f'Could not check disk space: {str(e)}',
            'timestamp': timezone.now()
        }


def _check_memory(health_check):
    """Check memory usage"""
    try:
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        if memory_percent > 90:
            status = 'critical'
            message = f'Memory usage critically high: {memory_percent:.1f}%'
        elif memory_percent > 80:
            status = 'warning'
            message = f'Memory usage high: {memory_percent:.1f}%'
        else:
            status = 'healthy'
            message = f'Memory usage OK: {memory_percent:.1f}%'
        
        return {
            'check_name': health_check.name,
            'status': status,
            'response_time': 0.01,
            'message': message,
            'timestamp': timezone.now()
        }
        
    except Exception as e:
        return {
            'check_name': health_check.name,
            'status': 'unknown',
            'response_time': None,
            'message': f'Could not check memory usage: {str(e)}',
            'timestamp': timezone.now()
        }


def create_system_alert(alert_type, priority, title, message, component=None, metadata=None):
    """Create a system alert"""
    alert = SystemAlert.objects.create(
        alert_type=alert_type,
        priority=priority,
        title=title,
        message=message,
        component=component,
        metadata=metadata or {}
    )
    
    logger.info(f"System alert created: {title} ({priority})")
    return alert


def log_error(error_type, message, user=None, component=None, request_path=None, 
              request_method=None, stack_trace=None, metadata=None):
    """Log an error"""
    error = ErrorLog.objects.create(
        error_type=error_type,
        message=message,
        user=user,
        component=component,
        request_path=request_path,
        request_method=request_method,
        stack_trace=stack_trace,
        metadata=metadata or {}
    )
    
    logger.error(f"Error logged: {error_type} - {message}")
    return error


def record_performance_metric(metric_type, value, unit=None, component=None, metadata=None):
    """Record a performance metric"""
    metric = PerformanceMetric.objects.create(
        metric_type=metric_type,
        value=value,
        unit=unit,
        component=component,
        metadata=metadata or {}
    )
    
    return metric
