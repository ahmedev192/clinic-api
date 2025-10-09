"""
Audit Trail Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
import json


class AuditLog(TimeStampedModel):
    """Audit trail for all model changes"""
    ACTION_TYPES = [
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('view', _('View')),
    ]
    
    # User and Session Information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                           verbose_name=_('User'))
    session_key = models.CharField(max_length=40, blank=True, verbose_name=_('Session Key'))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP Address'))
    user_agent = models.TextField(blank=True, verbose_name=_('User Agent'))
    
    # Object Information
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, 
                                   verbose_name=_('Content Type'))
    object_id = models.PositiveIntegerField(verbose_name=_('Object ID'))
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Action Details
    action = models.CharField(max_length=10, choices=ACTION_TYPES, verbose_name=_('Action'))
    object_repr = models.CharField(max_length=200, verbose_name=_('Object Representation'))
    
    # Change Details
    changes = models.JSONField(default=dict, verbose_name=_('Changes'))
    old_values = models.JSONField(default=dict, verbose_name=_('Old Values'))
    new_values = models.JSONField(default=dict, verbose_name=_('New Values'))
    
    # Additional Information
    reason = models.TextField(blank=True, verbose_name=_('Reason'))
    module = models.CharField(max_length=50, blank=True, verbose_name=_('Module'))
    
    class Meta:
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-created']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'created']),
            models.Index(fields=['action']),
            models.Index(fields=['created']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.object_repr} - {self.created}"


class AuditMiddleware:
    """Middleware to automatically log user actions"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Store request for use in signal handlers
        request._audit_request = request
        response = self.get_response(request)
        return response
