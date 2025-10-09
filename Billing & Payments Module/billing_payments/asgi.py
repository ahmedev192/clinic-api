"""
ASGI config for billing_payments project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'billing_payments.settings')

application = get_asgi_application()
