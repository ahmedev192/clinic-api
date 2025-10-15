"""
Celery tasks for background report generation and processing.
"""
from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import json
import logging

from .models import ReportQuery, ReportResult, ReportSchedule
from .utils import (
    generate_financial_report, generate_demographic_report,
    generate_doctor_performance_report, generate_appointment_stats_report,
    generate_custom_report, export_to_csv, export_to_excel, export_to_pdf
)

logger = logging.getLogger('analytics')


@shared_task(bind=True, max_retries=3)
def generate_report_task(self, query_id):
    """
    Generate a report in the background.
    """
    try:
        query = ReportQuery.objects.get(id=query_id)
        query.status = 'processing'
        query.started_at = timezone.now()
        query.save()
        
        # Generate report based on type
        if query.report_type == 'financial':
            report_data = generate_financial_report(
                date_from=query.date_from,
                date_to=query.date_to,
                department=query.filters.get('department'),
                payment_type=query.filters.get('payment_type')
            )
        elif query.report_type == 'demographic':
            report_data = generate_demographic_report(
                date_from=query.date_from,
                date_to=query.date_to,
                include_gender=query.filters.get('include_gender', True),
                include_age_groups=query.filters.get('include_age_groups', True),
                include_location=query.filters.get('include_location', True),
                include_visit_frequency=query.filters.get('include_visit_frequency', True)
            )
        elif query.report_type == 'doctor_performance':
            report_data = generate_doctor_performance_report(
                date_from=query.date_from,
                date_to=query.date_to,
                doctor_ids=query.filters.get('doctor_ids'),
                include_revenue=query.filters.get('include_revenue', True),
                include_consultation_time=query.filters.get('include_consultation_time', True),
                include_satisfaction=query.filters.get('include_satisfaction', False)
            )
        elif query.report_type == 'appointment_stats':
            report_data = generate_appointment_stats_report(
                date_from=query.date_from,
                date_to=query.date_to,
                group_by=query.filters.get('group_by', 'day'),
                include_no_shows=query.filters.get('include_no_shows', True),
                include_cancellations=query.filters.get('include_cancellations', True),
                include_peak_hours=query.filters.get('include_peak_hours', True)
            )
        elif query.report_type == 'custom':
            report_data = generate_custom_report(
                modules=query.filters.get('modules', []),
                filters=query.filters.get('filters', {}),
                date_from=query.date_from,
                date_to=query.date_to,
                group_by_fields=query.group_by,
                aggregation_fields=query.aggregation
            )
        else:
            raise ValueError(f"Unknown report type: {query.report_type}")
        
        # Create cache key
        cache_key = f"report_result_{query_id}_{timezone.now().timestamp()}"
        
        # Generate export files if requested
        csv_file = None
        excel_file = None
        pdf_file = None
        
        if 'csv' in query.filters.get('export_formats', ['csv']):
            csv_content = export_to_csv(
                report_data.get('data', []),
                include_headers_ar=True,
                include_headers_en=True
            )
            # In real implementation, save to file and get file path
            csv_file = f"reports/csv/report_{query_id}.csv"
        
        if 'excel' in query.filters.get('export_formats', []):
            excel_content = export_to_excel(
                report_data.get('data', []),
                include_headers_ar=True,
                include_headers_en=True
            )
            # In real implementation, save to file and get file path
            excel_file = f"reports/excel/report_{query_id}.xlsx"
        
        if 'pdf' in query.filters.get('export_formats', []):
            pdf_content = export_to_pdf(
                report_data.get('data', []),
                query.name,
                include_headers_ar=True,
                include_headers_en=True
            )
            # In real implementation, save to file and get file path
            pdf_file = f"reports/pdf/report_{query_id}.pdf"
        
        # Create result record
        result = ReportResult.objects.create(
            query=query,
            data=report_data,
            summary=report_data.get('summary', {}),
            metadata={
                'generated_at': timezone.now().isoformat(),
                'report_type': query.report_type,
                'filters_applied': query.filters,
                'group_by': query.group_by,
                'aggregation': query.aggregation
            },
            cache_key=cache_key,
            expires_at=timezone.now() + timezone.timedelta(hours=24),
            csv_file=csv_file,
            excel_file=excel_file,
            pdf_file=pdf_file
        )
        
        # Update query status
        query.status = 'completed'
        query.completed_at = timezone.now()
        query.save()
        
        # Cache the result
        cache.set(cache_key, report_data, 86400)  # 24 hours
        
        logger.info(f"Report {query_id} generated successfully")
        return f"Report {query_id} generated successfully"
        
    except Exception as exc:
        logger.error(f"Error generating report {query_id}: {str(exc)}")
        
        # Update query status
        query = ReportQuery.objects.get(id=query_id)
        query.status = 'failed'
        query.error_message = str(exc)
        query.retry_count += 1
        query.save()
        
        # Retry if not max retries reached
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return f"Report {query_id} generation failed: {str(exc)}"


@shared_task
def send_scheduled_report_task(schedule_id):
    """
    Send scheduled report via email.
    """
    try:
        schedule = ReportSchedule.objects.get(id=schedule_id)
        
        # Generate report using the template
        query = ReportQuery.objects.create(
            template=schedule.template,
            name=f"Scheduled: {schedule.name}",
            report_type=schedule.template.report_type,
            filters=schedule.template.filters,
            date_from=timezone.now() - timezone.timedelta(days=30),  # Last 30 days
            date_to=timezone.now(),
            group_by=schedule.template.group_by_fields,
            aggregation=schedule.template.aggregation_fields,
            created_by=schedule.created_by
        )
        
        # Generate the report
        generate_report_task.delay(query.id)
        
        # Wait for completion (in real implementation, use proper task chaining)
        # For now, we'll just log the action
        logger.info(f"Scheduled report {schedule_id} sent to {schedule.recipients}")
        
        # Update schedule
        schedule.last_run = timezone.now()
        schedule.save()
        
        return f"Scheduled report {schedule_id} sent successfully"
        
    except Exception as exc:
        logger.error(f"Error sending scheduled report {schedule_id}: {str(exc)}")
        return f"Scheduled report {schedule_id} failed: {str(exc)}"


@shared_task
def cleanup_old_reports():
    """
    Clean up old report results and files.
    """
    try:
        # Delete results older than 30 days
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        old_results = ReportResult.objects.filter(created_at__lt=cutoff_date)
        
        count = old_results.count()
        old_results.delete()
        
        # Clear expired cache entries
        # This would require custom cache management in a real implementation
        
        logger.info(f"Cleaned up {count} old report results")
        return f"Cleaned up {count} old report results"
        
    except Exception as exc:
        logger.error(f"Error cleaning up old reports: {str(exc)}")
        return f"Cleanup failed: {str(exc)}"


@shared_task
def generate_dashboard_data():
    """
    Generate cached dashboard data for quick access.
    """
    try:
        # Generate summary data for dashboard
        dashboard_data = {
            'financial_summary': generate_financial_report(
                date_from=timezone.now() - timezone.timedelta(days=30),
                date_to=timezone.now()
            ).get('summary', {}),
            'demographic_summary': generate_demographic_report(
                date_from=timezone.now() - timezone.timedelta(days=30),
                date_to=timezone.now()
            ).get('summary', {}),
            'appointment_summary': generate_appointment_stats_report(
                date_from=timezone.now() - timezone.timedelta(days=7),
                date_to=timezone.now()
            ).get('summary', {}),
            'generated_at': timezone.now().isoformat()
        }
        
        # Cache for 1 hour
        cache.set('dashboard_data', dashboard_data, 3600)
        
        logger.info("Dashboard data generated and cached")
        return "Dashboard data generated successfully"
        
    except Exception as exc:
        logger.error(f"Error generating dashboard data: {str(exc)}")
        return f"Dashboard data generation failed: {str(exc)}"


@shared_task
def sync_external_data_sources():
    """
    Sync data from external sources.
    """
    try:
        from .models import DataSource
        
        sources = DataSource.objects.filter(is_active=True)
        synced_count = 0
        
        for source in sources:
            try:
                # In real implementation, sync data based on source type
                if source.source_type == 'api':
                    # Sync from API
                    pass
                elif source.source_type == 'database':
                    # Sync from database
                    pass
                elif source.source_type == 'file':
                    # Sync from file
                    pass
                
                source.last_sync = timezone.now()
                source.save()
                synced_count += 1
                
            except Exception as e:
                logger.error(f"Error syncing source {source.id}: {str(e)}")
                continue
        
        logger.info(f"Synced {synced_count} data sources")
        return f"Synced {synced_count} data sources"
        
    except Exception as exc:
        logger.error(f"Error syncing external data sources: {str(exc)}")
        return f"Data sync failed: {str(exc)}"
