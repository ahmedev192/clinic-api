"""
Utility functions for notifications app
"""
import logging
from django.utils import timezone
from django.template import Template, Context
from apps.accounts.models import User
from .models import (
    Notification, NotificationTemplate, AlertThreshold, 
    NotificationQueue, NotificationLog
)

logger = logging.getLogger('admin_dashboard')


def send_notification(recipient, title, message, notification_type='system', 
                     priority='medium', channel='dashboard', data=None):
    """Send a notification to a user"""
    try:
        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            channel=channel,
            data=data or {},
            status='pending'
        )
        
        # Add to queue for processing
        NotificationQueue.objects.create(
            notification=notification,
            scheduled_at=timezone.now()
        )
        
        logger.info(f"Notification created: {title} for {recipient.username}")
        return notification
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return None


def create_notification_from_template(template, recipient, variables=None):
    """Create a notification from a template"""
    try:
        # Render title and message with variables
        title_template = Template(template.title_template)
        message_template = Template(template.message_template)
        
        context = Context(variables or {})
        title = title_template.render(context)
        message = message_template.render(context)
        
        # Create notification
        notification = Notification.objects.create(
            template=template,
            recipient=recipient,
            title=title,
            message=message,
            notification_type=template.notification_type,
            priority=template.priority,
            channel='dashboard',
            data=variables or {},
            status='pending'
        )
        
        # Add to queue for processing
        NotificationQueue.objects.create(
            notification=notification,
            scheduled_at=timezone.now()
        )
        
        logger.info(f"Notification created from template: {template.name} for {recipient.username}")
        return notification
        
    except Exception as e:
        logger.error(f"Error creating notification from template: {str(e)}")
        return None


def check_alert_thresholds():
    """Check all alert thresholds and generate notifications if needed"""
    try:
        results = []
        active_thresholds = AlertThreshold.objects.filter(is_active=True)
        
        for threshold in active_thresholds:
            # This would check actual metric values against thresholds
            # For now, we'll use mock data
            current_value = get_mock_metric_value(threshold.metric_type)
            
            if evaluate_threshold(current_value, threshold.threshold_value, threshold.comparison_operator):
                # Threshold exceeded, create notification
                notification = create_notification_from_template(
                    threshold.notification_template,
                    get_system_user(),  # System user for automated notifications
                    {
                        'metric_type': threshold.metric_type,
                        'current_value': current_value,
                        'threshold_value': threshold.threshold_value,
                        'threshold_name': threshold.name
                    }
                )
                
                if notification:
                    results.append({
                        'threshold': threshold.name,
                        'metric_type': threshold.metric_type,
                        'current_value': current_value,
                        'threshold_value': threshold.threshold_value,
                        'notification_created': True
                    })
        
        logger.info(f"Checked {len(active_thresholds)} thresholds, {len(results)} alerts triggered")
        return results
        
    except Exception as e:
        logger.error(f"Error checking alert thresholds: {str(e)}")
        return []


def evaluate_threshold(current_value, threshold_value, operator):
    """Evaluate if a threshold condition is met"""
    try:
        if operator == 'gt':
            return current_value > threshold_value
        elif operator == 'gte':
            return current_value >= threshold_value
        elif operator == 'lt':
            return current_value < threshold_value
        elif operator == 'lte':
            return current_value <= threshold_value
        elif operator == 'eq':
            return current_value == threshold_value
        elif operator == 'ne':
            return current_value != threshold_value
        else:
            return False
    except Exception as e:
        logger.error(f"Error evaluating threshold: {str(e)}")
        return False


def get_mock_metric_value(metric_type):
    """Get mock metric value for testing thresholds"""
    # This would be replaced with actual metric retrieval
    mock_values = {
        'inventory_stock': 15,
        'appointment_capacity': 85,
        'revenue_target': 120000,
        'error_rate': 2.5,
        'response_time': 1.8,
        'patient_wait_time': 25
    }
    return mock_values.get(metric_type, 0)


def get_system_user():
    """Get or create a system user for automated notifications"""
    try:
        user, created = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@clinic.com',
                'first_name': 'System',
                'last_name': 'User',
                'is_active': True
            }
        )
        return user
    except Exception as e:
        logger.error(f"Error getting system user: {str(e)}")
        return None


def process_notification_queue():
    """Process pending notifications in the queue"""
    try:
        results = []
        pending_notifications = NotificationQueue.objects.filter(
            status='pending',
            scheduled_at__lte=timezone.now()
        )[:10]  # Process up to 10 at a time
        
        for queue_item in pending_notifications:
            try:
                # Update status to processing
                queue_item.status = 'processing'
                queue_item.attempts += 1
                queue_item.last_attempt_at = timezone.now()
                queue_item.save()
                
                # Process the notification
                success = process_single_notification(queue_item.notification)
                
                if success:
                    queue_item.status = 'completed'
                    results.append({
                        'notification_id': queue_item.notification.id,
                        'status': 'completed'
                    })
                else:
                    if queue_item.attempts >= queue_item.max_attempts:
                        queue_item.status = 'failed'
                        queue_item.error_message = 'Max attempts exceeded'
                    else:
                        queue_item.status = 'pending'
                        # Reschedule for later
                        queue_item.scheduled_at = timezone.now() + timezone.timedelta(minutes=5)
                    
                    results.append({
                        'notification_id': queue_item.notification.id,
                        'status': queue_item.status
                    })
                
                queue_item.save()
                
            except Exception as e:
                logger.error(f"Error processing notification {queue_item.id}: {str(e)}")
                queue_item.status = 'failed'
                queue_item.error_message = str(e)
                queue_item.save()
                
                results.append({
                    'notification_id': queue_item.notification.id,
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"Processed {len(pending_notifications)} notifications from queue")
        return results
        
    except Exception as e:
        logger.error(f"Error processing notification queue: {str(e)}")
        return []


def process_single_notification(notification):
    """Process a single notification"""
    try:
        # Update notification status
        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.save()
        
        # Log the delivery attempt
        NotificationLog.objects.create(
            notification=notification,
            channel=notification.channel,
            status='sent',
            response_data={'processed_at': timezone.now().isoformat()}
        )
        
        # In a real implementation, this would:
        # - Send email if channel is 'email'
        # - Send SMS if channel is 'sms'
        # - Send push notification if channel is 'push'
        # - Call webhook if channel is 'webhook'
        # - Update dashboard if channel is 'dashboard'
        
        logger.info(f"Notification {notification.id} processed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error processing notification {notification.id}: {str(e)}")
        
        # Log the failed attempt
        NotificationLog.objects.create(
            notification=notification,
            channel=notification.channel,
            status='failed',
            error_message=str(e)
        )
        
        return False


def create_bulk_notifications(recipients, title, message, notification_type='system', 
                            priority='medium', channel='dashboard', data=None):
    """Create multiple notifications at once"""
    try:
        notifications = []
        
        for recipient in recipients:
            notification = Notification.objects.create(
                recipient=recipient,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                channel=channel,
                data=data or {},
                status='pending'
            )
            
            # Add to queue
            NotificationQueue.objects.create(
                notification=notification,
                scheduled_at=timezone.now()
            )
            
            notifications.append(notification)
        
        logger.info(f"Created {len(notifications)} bulk notifications")
        return notifications
        
    except Exception as e:
        logger.error(f"Error creating bulk notifications: {str(e)}")
        return []


def get_user_notifications(user, limit=50, unread_only=False):
    """Get notifications for a specific user"""
    try:
        queryset = Notification.objects.filter(recipient=user)
        
        if unread_only:
            queryset = queryset.filter(read_at__isnull=True)
        
        return queryset.order_by('-created_at')[:limit]
        
    except Exception as e:
        logger.error(f"Error getting user notifications: {str(e)}")
        return []


def cleanup_old_notifications(days=30):
    """Clean up old notifications"""
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        # Delete old notifications
        deleted_count = Notification.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['read', 'failed']
        ).delete()[0]
        
        # Delete old queue items
        queue_deleted_count = NotificationQueue.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['completed', 'failed']
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} notifications and {queue_deleted_count} queue items")
        return {
            'notifications_deleted': deleted_count,
            'queue_items_deleted': queue_deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old notifications: {str(e)}")
        return {'error': str(e)}

