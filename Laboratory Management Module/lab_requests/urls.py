from django.urls import path
from . import views

app_name = 'lab_requests'

urlpatterns = [
    # Lab Requests
    path('requests/', views.LabRequestListCreateView.as_view(), name='request-list-create'),
    path('requests/<int:pk>/', views.LabRequestDetailView.as_view(), name='request-detail'),
    path('requests/<int:pk>/status/', views.update_request_status, name='update-request-status'),
    
    # Request Items
    path('items/<int:item_id>/status/', views.update_item_status, name='update-item-status'),
    
    # Filtered Views
    path('requests/patient/<str:patient_id>/', views.get_requests_by_patient, name='requests-by-patient'),
    path('requests/doctor/<str:doctor_id>/', views.get_requests_by_doctor, name='requests-by-doctor'),
    path('requests/pending/', views.get_pending_requests, name='pending-requests'),
]
