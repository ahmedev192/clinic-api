from django.urls import path
from . import views

app_name = 'lab_samples'

urlpatterns = [
    # Samples
    path('samples/', views.SampleListCreateView.as_view(), name='sample-list-create'),
    path('samples/<int:pk>/', views.SampleDetailView.as_view(), name='sample-detail'),
    path('samples/<int:pk>/status/', views.update_sample_status, name='update-sample-status'),
    
    # Sample Collections
    path('collections/', views.SampleCollectionListCreateView.as_view(), name='collection-list-create'),
    
    # Search and Filter
    path('samples/search/', views.search_samples, name='search-samples'),
    path('samples/status/<str:status>/', views.get_samples_by_status, name='samples-by-status'),
    path('samples/expired/', views.get_expired_samples, name='expired-samples'),
]
