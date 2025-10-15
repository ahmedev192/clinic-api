"""
Audit signals for automatic logging
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.accounts.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import AuditLog
import json


def get_request():
    """Get the current request from thread local storage"""
    from django.utils.deprecation import MiddlewareMixin
    import threading
    
    if hasattr(threading.current_thread(), 'request'):
        return threading.current_thread().request
    return None


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    """Log model save operations"""
    # Skip logging for certain models
    if sender in [AuditLog, ContentType]:
        return
    
    request = get_request()
    user = None
    session_key = None
    ip_address = None
    user_agent = None
    
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
        session_key = request.session.session_key
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    action = 'create' if created else 'update'
    
    # Get changes for updates
    changes = {}
    old_values = {}
    new_values = {}
    
    if not created and hasattr(instance, '_state') and hasattr(instance._state, 'db'):
        # This is an update, try to get the old values
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            for field in instance._meta.fields:
                old_value = getattr(old_instance, field.name, None)
                new_value = getattr(instance, field.name, None)
                
                if old_value != new_value:
                    changes[field.name] = {
                        'old': str(old_value) if old_value is not None else None,
                        'new': str(new_value) if new_value is not None else None
                    }
                    old_values[field.name] = str(old_value) if old_value is not None else None
                    new_values[field.name] = str(new_value) if new_value is not None else None
        except sender.DoesNotExist:
            pass
    
    # Create audit log entry
    AuditLog.objects.create(
        user=user,
        session_key=session_key,
        ip_address=ip_address,
        user_agent=user_agent,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        action=action,
        object_repr=str(instance),
        changes=changes,
        old_values=old_values,
        new_values=new_values,
        module=instance._meta.app_label,
    )


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """Log model delete operations"""
    # Skip logging for certain models
    if sender in [AuditLog, ContentType]:
        return
    
    request = get_request()
    user = None
    session_key = None
    ip_address = None
    user_agent = None
    
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
        session_key = request.session.session_key
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Create audit log entry
    AuditLog.objects.create(
        user=user,
        session_key=session_key,
        ip_address=ip_address,
        user_agent=user_agent,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        action='delete',
        object_repr=str(instance),
        changes={},
        old_values={},
        new_values={},
        module=instance._meta.app_label,
    )

