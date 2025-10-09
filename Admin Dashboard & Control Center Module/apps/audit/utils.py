"""
Utility functions for audit app
"""
import logging
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    AuditLog, SystemLog, SecurityEvent, DataAccessLog, 
    ComplianceReport, AuditConfiguration
)

logger = logging.getLogger('admin_dashboard')


def log_audit_event(user, action_type, resource_type, description, 
                   resource_id=None, old_values=None, new_values=None, 
                   metadata=None, ip_address=None, user_agent=None, 
                   request_path=None, request_method=None, result='success'):
    """Log an audit event"""
    try:
        audit_log = AuditLog.objects.create(
            user=user,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            result=result,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            request_method=request_method,
            old_values=old_values or {},
            new_values=new_values or {},
            metadata=metadata or {}
        )
        
        logger.info(f"Audit event logged: {action_type} {resource_type} by {user.username if user else 'System'}")
        return audit_log
        
    except Exception as e:
        logger.error(f"Error logging audit event: {str(e)}")
        return None


def log_system_event(level, component, message, details=None, user=None, 
                    request_id=None, ip_address=None):
    """Log a system event"""
    try:
        system_log = SystemLog.objects.create(
            level=level,
            component=component,
            message=message,
            details=details or {},
            user=user,
            request_id=request_id,
            ip_address=ip_address
        )
        
        logger.info(f"System event logged: {level} - {component}: {message}")
        return system_log
        
    except Exception as e:
        logger.error(f"Error logging system event: {str(e)}")
        return None


def log_security_event(event_type, severity, title, description, user=None,
                      ip_address=None, user_agent=None, request_path=None,
                      metadata=None):
    """Log a security event"""
    try:
        security_event = SecurityEvent.objects.create(
            event_type=event_type,
            severity=severity,
            title=title,
            description=description,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            metadata=metadata or {}
        )
        
        logger.warning(f"Security event logged: {title} ({severity})")
        return security_event
        
    except Exception as e:
        logger.error(f"Error logging security event: {str(e)}")
        return None


def log_data_access(user, access_type, resource_type, resource_id=None,
                   resource_name=None, ip_address=None, user_agent=None,
                   request_path=None, data_fields=None, purpose=None):
    """Log data access"""
    try:
        data_access_log = DataAccessLog.objects.create(
            user=user,
            access_type=access_type,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            data_fields=data_fields or [],
            purpose=purpose
        )
        
        logger.info(f"Data access logged: {user.username} {access_type} {resource_type}")
        return data_access_log
        
    except Exception as e:
        logger.error(f"Error logging data access: {str(e)}")
        return None


def generate_compliance_report(report_type, period_start, period_end, name,
                             generated_by, metadata=None):
    """Generate a compliance report"""
    try:
        # Create report record
        report = ComplianceReport.objects.create(
            name=name,
            report_type=report_type,
            status='generating',
            period_start=period_start,
            period_end=period_end,
            generated_by=generated_by,
            metadata=metadata or {}
        )
        
        # Generate report data based on type
        if report_type == 'hipaa':
            report_data = generate_hipaa_report(period_start, period_end)
        elif report_type == 'gdpr':
            report_data = generate_gdpr_report(period_start, period_end)
        elif report_type == 'sox':
            report_data = generate_sox_report(period_start, period_end)
        else:
            report_data = generate_generic_report(period_start, period_end)
        
        # Update report with generated data
        report.summary = report_data.get('summary', {})
        report.findings = report_data.get('findings', [])
        report.recommendations = report_data.get('recommendations', [])
        report.status = 'completed'
        report.generated_at = timezone.now()
        report.file_path = f"/reports/compliance_{report.id}_{report_type}.pdf"
        report.file_size = 1024  # Mock file size
        report.save()
        
        logger.info(f"Compliance report generated: {name} ({report_type})")
        return report
        
    except Exception as e:
        logger.error(f"Error generating compliance report: {str(e)}")
        return None


def generate_hipaa_report(period_start, period_end):
    """Generate HIPAA compliance report"""
    try:
        # Get audit logs for the period
        audit_logs = AuditLog.objects.filter(
            timestamp__gte=period_start,
            timestamp__lte=period_end,
            resource_type__in=['patient', 'medical_record', 'billing']
        )
        
        # Get data access logs
        data_access_logs = DataAccessLog.objects.filter(
            timestamp__gte=period_start,
            timestamp__lte=period_end,
            resource_type__in=['patient', 'medical_record']
        )
        
        # Get security events
        security_events = SecurityEvent.objects.filter(
            timestamp__gte=period_start,
            timestamp__lte=period_end
        )
        
        summary = {
            'total_audit_events': audit_logs.count(),
            'total_data_access': data_access_logs.count(),
            'total_security_events': security_events.count(),
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat()
        }
        
        findings = []
        recommendations = []
        
        # Check for unauthorized access
        unauthorized_access = security_events.filter(
            event_type='unauthorized_access'
        ).count()
        
        if unauthorized_access > 0:
            findings.append({
                'type': 'security',
                'severity': 'high',
                'description': f'{unauthorized_access} unauthorized access attempts detected'
            })
            recommendations.append('Review and strengthen access controls')
        
        # Check for data breaches
        data_breaches = security_events.filter(
            event_type='system_breach'
        ).count()
        
        if data_breaches > 0:
            findings.append({
                'type': 'security',
                'severity': 'critical',
                'description': f'{data_breaches} potential data breaches detected'
            })
            recommendations.append('Implement immediate security measures and notify authorities')
        
        return {
            'summary': summary,
            'findings': findings,
            'recommendations': recommendations
        }
        
    except Exception as e:
        logger.error(f"Error generating HIPAA report: {str(e)}")
        return {'summary': {}, 'findings': [], 'recommendations': []}


def generate_gdpr_report(period_start, period_end):
    """Generate GDPR compliance report"""
    try:
        # Get data access logs
        data_access_logs = DataAccessLog.objects.filter(
            timestamp__gte=period_start,
            timestamp__lte=period_end
        )
        
        # Get audit logs for data modifications
        data_modifications = AuditLog.objects.filter(
            timestamp__gte=period_start,
            timestamp__lte=period_end,
            action_type__in=['create', 'update', 'delete'],
            resource_type__in=['patient', 'personal_data']
        )
        
        summary = {
            'total_data_access': data_access_logs.count(),
            'total_data_modifications': data_modifications.count(),
            'unique_users': data_access_logs.values('user').distinct().count(),
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat()
        }
        
        findings = []
        recommendations = []
        
        # Check for data retention compliance
        old_data_access = data_access_logs.filter(
            timestamp__lt=period_start - timezone.timedelta(days=365)
        ).count()
        
        if old_data_access > 0:
            findings.append({
                'type': 'compliance',
                'severity': 'medium',
                'description': f'{old_data_access} accesses to data older than retention period'
            })
            recommendations.append('Review data retention policies and implement automated cleanup')
        
        return {
            'summary': summary,
            'findings': findings,
            'recommendations': recommendations
        }
        
    except Exception as e:
        logger.error(f"Error generating GDPR report: {str(e)}")
        return {'summary': {}, 'findings': [], 'recommendations': []}


def generate_sox_report(period_start, period_end):
    """Generate SOX compliance report"""
    try:
        # Get financial audit logs
        financial_logs = AuditLog.objects.filter(
            timestamp__gte=period_start,
            timestamp__lte=period_end,
            resource_type__in=['billing', 'payment', 'financial']
        )
        
        # Get system logs for financial systems
        system_logs = SystemLog.objects.filter(
            timestamp__gte=period_start,
            timestamp__lte=period_end,
            component__in=['billing', 'analytics']
        )
        
        summary = {
            'total_financial_events': financial_logs.count(),
            'total_system_events': system_logs.count(),
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat()
        }
        
        findings = []
        recommendations = []
        
        # Check for financial data integrity
        failed_financial_operations = financial_logs.filter(
            result='failure'
        ).count()
        
        if failed_financial_operations > 0:
            findings.append({
                'type': 'integrity',
                'severity': 'high',
                'description': f'{failed_financial_operations} failed financial operations'
            })
            recommendations.append('Investigate and resolve financial operation failures')
        
        return {
            'summary': summary,
            'findings': findings,
            'recommendations': recommendations
        }
        
    except Exception as e:
        logger.error(f"Error generating SOX report: {str(e)}")
        return {'summary': {}, 'findings': [], 'recommendations': []}


def generate_generic_report(period_start, period_end):
    """Generate generic compliance report"""
    try:
        # Get all audit logs for the period
        audit_logs = AuditLog.objects.filter(
            timestamp__gte=period_start,
            timestamp__lte=period_end
        )
        
        # Get security events
        security_events = SecurityEvent.objects.filter(
            timestamp__gte=period_start,
            timestamp__lte=period_end
        )
        
        summary = {
            'total_audit_events': audit_logs.count(),
            'total_security_events': security_events.count(),
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat()
        }
        
        findings = []
        recommendations = []
        
        # Check for high-severity security events
        high_severity_events = security_events.filter(
            severity__in=['high', 'critical']
        ).count()
        
        if high_severity_events > 0:
            findings.append({
                'type': 'security',
                'severity': 'high',
                'description': f'{high_severity_events} high-severity security events'
            })
            recommendations.append('Review and address high-severity security events')
        
        return {
            'summary': summary,
            'findings': findings,
            'recommendations': recommendations
        }
        
    except Exception as e:
        logger.error(f"Error generating generic report: {str(e)}")
        return {'summary': {}, 'findings': [], 'recommendations': []}


def cleanup_old_logs(retention_days=365):
    """Clean up old logs based on retention policy"""
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=retention_days)
        
        # Clean up old audit logs
        audit_deleted = AuditLog.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        # Clean up old system logs
        system_deleted = SystemLog.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        # Clean up old data access logs
        data_access_deleted = DataAccessLog.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        # Keep security events longer (2 years)
        security_cutoff = timezone.now() - timezone.timedelta(days=730)
        security_deleted = SecurityEvent.objects.filter(
            timestamp__lt=security_cutoff,
            is_resolved=True
        ).delete()[0]
        
        logger.info(f"Cleaned up {audit_deleted} audit logs, {system_deleted} system logs, "
                   f"{data_access_deleted} data access logs, {security_deleted} security events")
        
        return {
            'audit_logs_deleted': audit_deleted,
            'system_logs_deleted': system_deleted,
            'data_access_logs_deleted': data_access_deleted,
            'security_events_deleted': security_deleted,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old logs: {str(e)}")
        return {'error': str(e)}


def get_audit_configuration(component):
    """Get audit configuration for a component"""
    try:
        config, created = AuditConfiguration.objects.get_or_create(
            component=component,
            defaults={
                'is_enabled': True,
                'log_level': 'INFO',
                'retention_days': 365,
                'log_actions': ['create', 'update', 'delete'],
                'exclude_users': []
            }
        )
        return config
    except Exception as e:
        logger.error(f"Error getting audit configuration: {str(e)}")
        return None


def should_log_event(component, action_type, user):
    """Check if an event should be logged based on configuration"""
    try:
        config = get_audit_configuration(component)
        if not config or not config.is_enabled:
            return False
        
        if action_type not in config.log_actions:
            return False
        
        if user and user.username in config.exclude_users:
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking if event should be logged: {str(e)}")
        return True  # Default to logging if there's an error


def get_user_activity_summary(user, days=30):
    """Get activity summary for a user"""
    try:
        since = timezone.now() - timezone.timedelta(days=days)
        
        # Get user's audit logs
        audit_logs = AuditLog.objects.filter(
            user=user,
            timestamp__gte=since
        )
        
        # Get data access logs
        data_access_logs = DataAccessLog.objects.filter(
            user=user,
            timestamp__gte=since
        )
        
        # Get security events involving the user
        security_events = SecurityEvent.objects.filter(
            user=user,
            timestamp__gte=since
        )
        
        summary = {
            'user': user.username,
            'period_days': days,
            'total_actions': audit_logs.count(),
            'data_access_count': data_access_logs.count(),
            'security_events': security_events.count(),
            'actions_by_type': dict(audit_logs.values('action_type').annotate(
                count=Count('id')
            ).values_list('action_type', 'count')),
            'last_activity': audit_logs.first().timestamp if audit_logs.exists() else None
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting user activity summary: {str(e)}")
        return {}
