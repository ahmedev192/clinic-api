from django.urls import path
from . import views

app_name = 'lab_tests'

urlpatterns = [
    # Test Categories
    path('categories/', views.TestCategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.TestCategoryDetailView.as_view(), name='category-detail'),
    
    # Lab Tests
    path('tests/', views.LabTestListCreateView.as_view(), name='test-list-create'),
    path('tests/<int:pk>/', views.LabTestDetailView.as_view(), name='test-detail'),
    path('tests/search/', views.search_tests, name='test-search'),
    path('tests/active/', views.active_tests, name='active-tests'),
]
