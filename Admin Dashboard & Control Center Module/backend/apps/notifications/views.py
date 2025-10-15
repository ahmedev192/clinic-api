from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import (
    NotificationTemplate, Notification, NotificationRule, 
    NotificationSubscription, NotificationLog, AlertThreshold, NotificationQueue
)
from .serializers import (
    NotificationTemplateSerializer, NotificationSerializer, NotificationRuleSerializer,
    NotificationSubscriptionSerializer, NotificationLogSerializer, AlertThresholdSerializer,
    NotificationQueueSerializer, NotificationSummarySerializer, NotificationStatsSerializer
)
from .utils import (
    send_notification, create_notification_from_template, 
    check_alert_thresholds, process_notification_queue
)

logger = logging.getLogger('admin_dashboard')


class NotificationTemplateListCreateView(generics.ListCreateAPIView):
    """List and create notification templates"""
    queryset = NotificationTemplate.objects.filter(is_active=True)
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        notification_type = self.request.query_params.get('notification_type')
        priority = self.request.query_params.get('priority')
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('name')


class NotificationListCreateView(generics.ListCreateAPIView):
    """List and create notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        recipient_id = self.request.query_params.get('recipient_id')
        notification_type = self.request.query_params.get('notification_type')
        status_filter = self.request.query_params.get('status')
        is_read = self.request.query_params.get('is_read')
        
        if recipient_id:
            queryset = queryset.filter(recipient_id=recipient_id)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if is_read is not None:
            if is_read.lower() == 'true':
                queryset = queryset.filter(read_at__isnull=False)
            else:
                queryset = queryset.filter(read_at__isnull=True)
        
        return queryset.order_by('-created_at')


class NotificationRuleListCreateView(generics.ListCreateAPIView):
    """List and create notification rules"""
    queryset = NotificationRule.objects.all()
    serializer_class = NotificationRuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        rule_type = self.request.query_params.get('rule_type')
        notification_type = self.request.query_params.get('notification_type')
        is_active = self.request.query_params.get('is_active')
        
        if rule_type:
            queryset = queryset.filter(rule_type=rule_type)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')


class NotificationSubscriptionListCreateView(generics.ListCreateAPIView):
    """List and create notification subscriptions"""
    queryset = NotificationSubscription.objects.all()
    serializer_class = NotificationSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        notification_type = self.request.query_params.get('notification_type')
        channel = self.request.query_params.get('channel')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if channel:
            queryset = queryset.filter(channel=channel)
        
        return queryset.order_by('user', 'notification_type')


class AlertThresholdListCreateView(generics.ListCreateAPIView):
    """List and create alert thresholds"""
    queryset = AlertThreshold.objects.all()
    serializer_class = AlertThresholdSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        metric_type = self.request.query_params.get('metric_type')
        is_active = self.request.query_params.get('is_active')
        
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')


class NotificationQueueListCreateView(generics.ListCreateAPIView):
    """List and create notification queue items"""
    queryset = NotificationQueue.objects.all()
    serializer_class = NotificationQueueSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('scheduled_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_summary(request):
    """Get notification summary for dashboard"""
    try:
        user = request.user
        days = int(request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=days)
        
        # Get notification counts
        total_notifications = Notification.objects.filter(recipient=user).count()
        unread_notifications = Notification.objects.filter(
            recipient=user, read_at__isnull=True
        ).count()
        pending_notifications = Notification.objects.filter(
            recipient=user, status='pending'
        ).count()
        failed_notifications = Notification.objects.filter(
            recipient=user, status='failed'
        ).count()
        
        # Get notifications by type
        notifications_by_type = Notification.objects.filter(
            recipient=user, created_at__gte=since
        ).values('notification_type').annotate(count=Count('id'))
        notifications_by_type = {item['notification_type']: item['count'] for item in notifications_by_type}
        
        # Get notifications by priority
        notifications_by_priority = Notification.objects.filter(
            recipient=user, created_at__gte=since
        ).values('priority').annotate(count=Count('id'))
        notifications_by_priority = {item['priority']: item['count'] for item in notifications_by_priority}
        
        summary_data = {
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'pending_notifications': pending_notifications,
            'failed_notifications': failed_notifications,
            'notifications_by_type': notifications_by_type,
            'notifications_by_priority': notifications_by_priority,
            'last_updated': timezone.now()
        }
        
        serializer = NotificationSummarySerializer(summary_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting notification summary: {str(e)}")
        return Response(
            {'error': f'Failed to get notification summary: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.status = 'read'
        notification.read_at = timezone.now()
        notification.save()
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
        
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        return Response(
            {'error': f'Failed to mark notification as read: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_as_read(request):
    """Mark all notifications as read for the current user"""
    try:
        updated_count = Notification.objects.filter(
            recipient=request.user, read_at__isnull=True
        ).update(
            status='read',
            read_at=timezone.now()
        )
        
        return Response({'message': f'{updated_count} notifications marked as read'})
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        return Response(
            {'error': f'Failed to mark all notifications as read: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification_api(request):
    """Send a notification via API"""
    try:
        recipient_id = request.data.get('recipient_id')
        title = request.data.get('title')
        message = request.data.get('message')
        notification_type = request.data.get('notification_type', 'system')
        priority = request.data.get('priority', 'medium')
        channel = request.data.get('channel', 'dashboard')
        data = request.data.get('data', {})
        
        if not all([recipient_id, title, message]):
            return Response(
                {'error': 'Recipient ID, title, and message are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth.models import User
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Recipient not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create and send notification
        notification = send_notification(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            channel=channel,
            data=data
        )
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return Response(
            {'error': f'Failed to send notification: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_from_template(request):
    """Create notification from template"""
    try:
        template_id = request.data.get('template_id')
        recipient_id = request.data.get('recipient_id')
        variables = request.data.get('variables', {})
        
        if not all([template_id, recipient_id]):
            return Response(
                {'error': 'Template ID and recipient ID are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            template = NotificationTemplate.objects.get(id=template_id)
        except NotificationTemplate.DoesNotExist:
            return Response(
                {'error': 'Template not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            from django.contrib.auth.models import User
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Recipient not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create notification from template
        notification = create_notification_from_template(template, recipient, variables)
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating notification from template: {str(e)}")
        return Response(
            {'error': f'Failed to create notification from template: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_thresholds(request):
    """Check alert thresholds and generate notifications"""
    try:
        results = check_alert_thresholds()
        return Response(results)
        
    except Exception as e:
        logger.error(f"Error checking thresholds: {str(e)}")
        return Response(
            {'error': f'Failed to check thresholds: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_queue(request):
    """Process notification queue"""
    try:
        results = process_notification_queue()
        return Response(results)
        
    except Exception as e:
        logger.error(f"Error processing queue: {str(e)}")
        return Response(
            {'error': f'Failed to process queue: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_stats(request):
    """Get notification statistics"""
    try:
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)
        
        # Get notification statistics
        total_sent = Notification.objects.filter(
            created_at__gte=since, status__in=['sent', 'delivered', 'read']
        ).count()
        
        total_delivered = Notification.objects.filter(
            created_at__gte=since, status__in=['delivered', 'read']
        ).count()
        
        total_read = Notification.objects.filter(
            created_at__gte=since, status='read'
        ).count()
        
        delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
        read_rate = (total_read / total_delivered * 100) if total_delivered > 0 else 0
        
        # Calculate average delivery time (mock data for now)
        average_delivery_time = 2.5  # seconds
        
        stats_data = {
            'period': f"Last {days} days",
            'total_sent': total_sent,
            'total_delivered': total_delivered,
            'total_read': total_read,
            'delivery_rate': round(delivery_rate, 2),
            'read_rate': round(read_rate, 2),
            'average_delivery_time': average_delivery_time,
            'generated_at': timezone.now()
        }
        
        serializer = NotificationStatsSerializer(stats_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {str(e)}")
        return Response(
            {'error': f'Failed to get notification stats: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
