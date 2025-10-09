"""
Utility functions for report generation and data processing.
"""
import pandas as pd
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Sum, Avg, Count, Min, Max
from django.core.cache import cache
from django.conf import settings
import io
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter


def generate_financial_report(date_from, date_to, department=None, payment_type=None):
    """
    Generate financial report with revenue, expenses, and profit summaries.
    """
    # This is a mock implementation - in real scenario, you'd query actual data
    # from billing, payments, and expense modules
    
    # Mock data for demonstration
    mock_data = {
        'summary': {
            'total_revenue': 150000.00,
            'outstanding_balances': 25000.00,
            'total_expenses': 75000.00,
            'net_profit': 75000.00,
            'currency': 'USD'
        },
        'revenue_by_payment_type': [
            {'payment_type': 'Cash', 'amount': 45000.00, 'percentage': 30.0},
            {'payment_type': 'Credit Card', 'amount': 60000.00, 'percentage': 40.0},
            {'payment_type': 'Insurance', 'amount': 45000.00, 'percentage': 30.0}
        ],
        'revenue_by_department': [
            {'department': 'Cardiology', 'amount': 45000.00, 'percentage': 30.0},
            {'department': 'Orthopedics', 'amount': 60000.00, 'percentage': 40.0},
            {'department': 'General Medicine', 'amount': 45000.00, 'percentage': 30.0}
        ],
        'monthly_trends': [
            {'month': '2024-01', 'revenue': 45000.00, 'expenses': 22000.00, 'profit': 23000.00},
            {'month': '2024-02', 'revenue': 52000.00, 'expenses': 25000.00, 'profit': 27000.00},
            {'month': '2024-03', 'revenue': 53000.00, 'expenses': 28000.00, 'profit': 25000.00}
        ],
        'outstanding_balances': [
            {'patient_id': 1, 'patient_name': 'John Doe', 'amount': 5000.00, 'days_overdue': 30},
            {'patient_id': 2, 'patient_name': 'Jane Smith', 'amount': 7500.00, 'days_overdue': 45},
            {'patient_id': 3, 'patient_name': 'Ahmed Ali', 'amount': 12000.00, 'days_overdue': 60}
        ],
        'expenses_breakdown': [
            {'category': 'Staff Salaries', 'amount': 40000.00, 'percentage': 53.3},
            {'category': 'Medical Supplies', 'amount': 15000.00, 'percentage': 20.0},
            {'category': 'Equipment', 'amount': 10000.00, 'percentage': 13.3},
            {'category': 'Utilities', 'amount': 10000.00, 'percentage': 13.3}
        ]
    }
    
    # Add bilingual labels
    mock_data['labels'] = {
        'en': {
            'total_revenue': 'Total Revenue',
            'outstanding_balances': 'Outstanding Balances',
            'total_expenses': 'Total Expenses',
            'net_profit': 'Net Profit',
            'revenue_by_payment_type': 'Revenue by Payment Type',
            'revenue_by_department': 'Revenue by Department',
            'monthly_trends': 'Monthly Trends',
            'outstanding_balances': 'Outstanding Balances',
            'expenses_breakdown': 'Expenses Breakdown'
        },
        'ar': {
            'total_revenue': 'إجمالي الإيرادات',
            'outstanding_balances': 'الرصيد المستحق',
            'total_expenses': 'إجمالي المصروفات',
            'net_profit': 'صافي الربح',
            'revenue_by_payment_type': 'الإيرادات حسب نوع الدفع',
            'revenue_by_department': 'الإيرادات حسب القسم',
            'monthly_trends': 'الاتجاهات الشهرية',
            'outstanding_balances': 'الرصيد المستحق',
            'expenses_breakdown': 'تفصيل المصروفات'
        }
    }
    
    return mock_data


def generate_demographic_report(date_from, date_to, include_gender=True, include_age_groups=True, 
                               include_location=True, include_visit_frequency=True):
    """
    Generate demographic report with patient statistics.
    """
    # Mock data for demonstration
    mock_data = {
        'summary': {
            'total_patients': 1250,
            'new_patients': 150,
            'returning_patients': 1100,
            'active_patients': 800
        }
    }
    
    if include_gender:
        mock_data['gender_distribution'] = [
            {'gender': 'Male', 'count': 650, 'percentage': 52.0},
            {'gender': 'Female', 'count': 600, 'percentage': 48.0}
        ]
    
    if include_age_groups:
        mock_data['age_groups'] = [
            {'age_group': '0-18', 'count': 200, 'percentage': 16.0},
            {'age_group': '19-35', 'count': 400, 'percentage': 32.0},
            {'age_group': '36-50', 'count': 350, 'percentage': 28.0},
            {'age_group': '51-65', 'count': 200, 'percentage': 16.0},
            {'age_group': '65+', 'count': 100, 'percentage': 8.0}
        ]
    
    if include_location:
        mock_data['location_distribution'] = [
            {'city': 'Riyadh', 'count': 500, 'percentage': 40.0},
            {'city': 'Jeddah', 'count': 300, 'percentage': 24.0},
            {'city': 'Dammam', 'count': 200, 'percentage': 16.0},
            {'city': 'Other', 'count': 250, 'percentage': 20.0}
        ]
    
    if include_visit_frequency:
        mock_data['visit_frequency'] = [
            {'frequency': '1 visit', 'count': 300, 'percentage': 24.0},
            {'frequency': '2-5 visits', 'count': 600, 'percentage': 48.0},
            {'frequency': '6-10 visits', 'count': 250, 'percentage': 20.0},
            {'frequency': '10+ visits', 'count': 100, 'percentage': 8.0}
        ]
    
    # Add bilingual labels
    mock_data['labels'] = {
        'en': {
            'total_patients': 'Total Patients',
            'new_patients': 'New Patients',
            'returning_patients': 'Returning Patients',
            'active_patients': 'Active Patients',
            'gender_distribution': 'Gender Distribution',
            'age_groups': 'Age Groups',
            'location_distribution': 'Location Distribution',
            'visit_frequency': 'Visit Frequency'
        },
        'ar': {
            'total_patients': 'إجمالي المرضى',
            'new_patients': 'مرضى جدد',
            'returning_patients': 'مرضى عائدون',
            'active_patients': 'مرضى نشطون',
            'gender_distribution': 'توزيع الجنس',
            'age_groups': 'الفئات العمرية',
            'location_distribution': 'توزيع المواقع',
            'visit_frequency': 'تكرار الزيارات'
        }
    }
    
    return mock_data


def generate_doctor_performance_report(date_from, date_to, doctor_ids=None, include_revenue=True,
                                      include_consultation_time=True, include_satisfaction=False):
    """
    Generate doctor performance report.
    """
    # Mock data for demonstration
    mock_data = {
        'summary': {
            'total_doctors': 15,
            'active_doctors': 12,
            'total_consultations': 2500,
            'average_consultation_time': 25.5
        },
        'doctor_performance': [
            {
                'doctor_id': 1,
                'doctor_name': 'Dr. Ahmed Al-Rashid',
                'specialization': 'Cardiology',
                'consultations': 200,
                'revenue': 45000.00,
                'average_consultation_time': 30.0,
                'satisfaction_score': 4.5 if include_satisfaction else None
            },
            {
                'doctor_id': 2,
                'doctor_name': 'Dr. Sarah Johnson',
                'specialization': 'Orthopedics',
                'consultations': 180,
                'revenue': 38000.00,
                'average_consultation_time': 25.0,
                'satisfaction_score': 4.8 if include_satisfaction else None
            },
            {
                'doctor_id': 3,
                'doctor_name': 'Dr. Mohammed Hassan',
                'specialization': 'General Medicine',
                'consultations': 220,
                'revenue': 32000.00,
                'average_consultation_time': 20.0,
                'satisfaction_score': 4.2 if include_satisfaction else None
            }
        ]
    }
    
    # Add bilingual labels
    mock_data['labels'] = {
        'en': {
            'total_doctors': 'Total Doctors',
            'active_doctors': 'Active Doctors',
            'total_consultations': 'Total Consultations',
            'average_consultation_time': 'Average Consultation Time (minutes)',
            'doctor_name': 'Doctor Name',
            'specialization': 'Specialization',
            'consultations': 'Consultations',
            'revenue': 'Revenue',
            'satisfaction_score': 'Satisfaction Score'
        },
        'ar': {
            'total_doctors': 'إجمالي الأطباء',
            'active_doctors': 'أطباء نشطون',
            'total_consultations': 'إجمالي الاستشارات',
            'average_consultation_time': 'متوسط وقت الاستشارة (دقيقة)',
            'doctor_name': 'اسم الطبيب',
            'specialization': 'التخصص',
            'consultations': 'الاستشارات',
            'revenue': 'الإيرادات',
            'satisfaction_score': 'درجة الرضا'
        }
    }
    
    return mock_data


def generate_appointment_stats_report(date_from, date_to, group_by='day', include_no_shows=True,
                                     include_cancellations=True, include_peak_hours=True):
    """
    Generate appointment statistics report.
    """
    # Mock data for demonstration
    mock_data = {
        'summary': {
            'total_appointments': 3000,
            'completed_appointments': 2700,
            'no_show_appointments': 200 if include_no_shows else 0,
            'cancelled_appointments': 100 if include_cancellations else 0,
            'no_show_rate': 6.7 if include_no_shows else 0,
            'cancellation_rate': 3.3 if include_cancellations else 0
        }
    }
    
    if group_by == 'day':
        mock_data['daily_stats'] = [
            {'date': '2024-01-01', 'total': 50, 'completed': 45, 'no_show': 3, 'cancelled': 2},
            {'date': '2024-01-02', 'total': 60, 'completed': 55, 'no_show': 3, 'cancelled': 2},
            {'date': '2024-01-03', 'total': 45, 'completed': 42, 'no_show': 2, 'cancelled': 1}
        ]
    elif group_by == 'week':
        mock_data['weekly_stats'] = [
            {'week': 'Week 1', 'total': 350, 'completed': 320, 'no_show': 20, 'cancelled': 10},
            {'week': 'Week 2', 'total': 380, 'completed': 350, 'no_show': 18, 'cancelled': 12},
            {'week': 'Week 3', 'total': 400, 'completed': 370, 'no_show': 22, 'cancelled': 8}
        ]
    elif group_by == 'month':
        mock_data['monthly_stats'] = [
            {'month': 'January', 'total': 1200, 'completed': 1100, 'no_show': 70, 'cancelled': 30},
            {'month': 'February', 'total': 1300, 'completed': 1200, 'no_show': 75, 'cancelled': 25},
            {'month': 'March', 'total': 1400, 'completed': 1300, 'no_show': 80, 'cancelled': 20}
        ]
    
    if include_peak_hours:
        mock_data['peak_hours'] = [
            {'hour': '09:00', 'appointments': 45, 'percentage': 15.0},
            {'hour': '10:00', 'appointments': 60, 'percentage': 20.0},
            {'hour': '11:00', 'appointments': 55, 'percentage': 18.3},
            {'hour': '14:00', 'appointments': 50, 'percentage': 16.7},
            {'hour': '15:00', 'appointments': 40, 'percentage': 13.3}
        ]
    
    # Add bilingual labels
    mock_data['labels'] = {
        'en': {
            'total_appointments': 'Total Appointments',
            'completed_appointments': 'Completed Appointments',
            'no_show_appointments': 'No-Show Appointments',
            'cancelled_appointments': 'Cancelled Appointments',
            'no_show_rate': 'No-Show Rate (%)',
            'cancellation_rate': 'Cancellation Rate (%)',
            'peak_hours': 'Peak Hours'
        },
        'ar': {
            'total_appointments': 'إجمالي المواعيد',
            'completed_appointments': 'المواعيد المكتملة',
            'no_show_appointments': 'المواعيد غير المحضورة',
            'cancelled_appointments': 'المواعيد الملغية',
            'no_show_rate': 'معدل عدم الحضور (%)',
            'cancellation_rate': 'معدل الإلغاء (%)',
            'peak_hours': 'ساعات الذروة'
        }
    }
    
    return mock_data


def generate_custom_report(modules, filters, date_from, date_to, group_by_fields, aggregation_fields):
    """
    Generate custom report based on specified modules and filters.
    """
    # This is a simplified implementation - in real scenario, you'd dynamically
    # query the specified modules and apply filters and aggregations
    
    mock_data = {
        'summary': {
            'modules_queried': modules,
            'date_range': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'total_records': 1500
        },
        'data': [
            {'field1': 'Value1', 'field2': 'Value2', 'count': 100, 'sum': 5000.00},
            {'field1': 'Value2', 'field2': 'Value3', 'count': 150, 'sum': 7500.00},
            {'field1': 'Value3', 'field2': 'Value1', 'count': 200, 'sum': 10000.00}
        ],
        'aggregations': aggregation_fields,
        'group_by': group_by_fields
    }
    
    # Add bilingual labels
    mock_data['labels'] = {
        'en': {
            'modules_queried': 'Modules Queried',
            'date_range': 'Date Range',
            'total_records': 'Total Records',
            'data': 'Data'
        },
        'ar': {
            'modules_queried': 'الوحدات المستعلامة',
            'date_range': 'نطاق التاريخ',
            'total_records': 'إجمالي السجلات',
            'data': 'البيانات'
        }
    }
    
    return mock_data


def export_to_csv(data, include_headers_ar=True, include_headers_en=True):
    """
    Export data to CSV format with bilingual headers.
    """
    df = pd.DataFrame(data)
    
    # Create bilingual headers
    if include_headers_ar and include_headers_en:
        # Add Arabic headers as first row
        arabic_headers = ['البيانات', 'القيم', 'العدد', 'المجموع']  # Mock Arabic headers
        df_ar = pd.DataFrame([arabic_headers], columns=df.columns)
        df = pd.concat([df_ar, df], ignore_index=True)
    
    # Convert to CSV
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    return output.getvalue()


def export_to_excel(data, include_headers_ar=True, include_headers_en=True):
    """
    Export data to Excel format with bilingual headers.
    """
    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Report Data"
    
    # Add data
    df = pd.DataFrame(data)
    
    # Add headers
    row = 1
    if include_headers_ar and include_headers_en:
        # Add Arabic headers
        arabic_headers = ['البيانات', 'القيم', 'العدد', 'المجموع']  # Mock Arabic headers
        for col, header in enumerate(arabic_headers, 1):
            cell = ws.cell(row=row, column=col, value=header)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        row += 1
    
    # Add English headers
    if include_headers_en:
        for col, header in enumerate(df.columns, 1):
            cell = ws.cell(row=row, column=col, value=str(header))
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        row += 1
    
    # Add data rows
    for r_idx, row_data in enumerate(df.itertuples(index=False), row):
        for c_idx, value in enumerate(row_data, 1):
            ws.cell(row=r_idx, column=c_idx, value=value)
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Save to bytes
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()


def export_to_pdf(data, title, include_headers_ar=True, include_headers_en=True):
    """
    Export data to PDF format with bilingual headers.
    """
    # Create PDF document
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Build content
    story = []
    
    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))
    
    # Convert data to table format
    df = pd.DataFrame(data)
    
    # Prepare table data
    table_data = []
    
    # Add headers
    if include_headers_ar and include_headers_en:
        arabic_headers = ['البيانات', 'القيم', 'العدد', 'المجموع']  # Mock Arabic headers
        table_data.append(arabic_headers)
    
    if include_headers_en:
        table_data.append(list(df.columns))
    
    # Add data rows
    for _, row in df.iterrows():
        table_data.append(list(row))
    
    # Create table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    # Build PDF
    doc.build(story)
    output.seek(0)
    return output.getvalue()
