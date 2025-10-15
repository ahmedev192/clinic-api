"""
WSGI config for clinic_analytics project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_analytics.settings')

application = get_wsgi_application()
