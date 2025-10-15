"""
OAuth2 app configuration.
"""
from django.apps import AppConfig


class Oauth2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.oauth2'
    verbose_name = 'OAuth2/OIDC SSO'

