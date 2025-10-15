from django.urls import path
from . import views

app_name = 'lab_results'

urlpatterns = [
    # Lab Results
    path('results/', views.LabResultListCreateView.as_view(), name='result-list-create'),
    path('results/<int:pk>/', views.LabResultDetailView.as_view(), name='result-detail'),
    path('results/<int:pk>/approve-reject/', views.approve_reject_result, name='approve-reject-result'),
    
    # Result Attachments
    path('results/<int:result_id>/attachments/', views.ResultAttachmentListCreateView.as_view(), name='result-attachments'),
    
    # Search and Filter
    path('results/search/', views.search_results, name='search-results'),
    path('results/critical/', views.get_critical_results, name='critical-results'),
    path('results/pending-approval/', views.get_pending_approval_results, name='pending-approval-results'),
    path('results/patient/<str:patient_id>/', views.get_results_by_patient, name='results-by-patient'),
]
