"""
OAuth2/OIDC URL patterns.
"""
from django.urls import path
from . import views

urlpatterns = [
    # OAuth2 providers
    path('providers/', views.OAuth2ProviderListView.as_view(), name='oauth2-provider-list'),
    path('providers/<uuid:pk>/', views.OAuth2ProviderDetailView.as_view(), name='oauth2-provider-detail'),
    
    # OAuth2 flow
    path('authorize/', views.OAuth2AuthorizeView.as_view(), name='oauth2-authorize'),
    path('callback/', views.OAuth2CallbackView.as_view(), name='oauth2-callback'),
    
    # Account management
    path('accounts/', views.ExternalAccountListView.as_view(), name='external-account-list'),
    path('accounts/link/', views.AccountLinkingView.as_view(), name='account-linking'),
    path('accounts/unlink/', views.AccountUnlinkingView.as_view(), name='account-unlinking'),
    
    # Session management
    path('sessions/', views.oauth2_sessions, name='oauth2-sessions'),
    path('sessions/revoke/', views.revoke_oauth2_session, name='oauth2-session-revoke'),
]

