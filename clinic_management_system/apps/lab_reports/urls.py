from django.urls import path
from . import views

app_name = 'lab_reports'

urlpatterns = [
    # Lab Reports
    path('reports/', views.LabReportListCreateView.as_view(), name='report-list-create'),
    path('reports/<int:pk>/', views.LabReportDetailView.as_view(), name='report-detail'),
    path('reports/<int:pk>/download/', views.download_report, name='download-report'),
    path('reports/<int:pk>/deliver/', views.deliver_report, name='deliver-report'),
    
    # Report Templates
    path('templates/', views.ReportTemplateListCreateView.as_view(), name='template-list-create'),
    path('templates/<int:pk>/', views.ReportTemplateDetailView.as_view(), name='template-detail'),
    
    # Report Generation and Search
    path('reports/generate/', views.generate_report, name='generate-report'),
    path('reports/search/', views.search_reports, name='search-reports'),
]
