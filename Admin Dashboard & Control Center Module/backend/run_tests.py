#!/usr/bin/env python
"""
Test runner script for the Admin Dashboard Module
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_dashboard.settings')
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests([
        "apps.dashboard",
        "apps.monitoring", 
        "apps.analytics",
        "apps.notifications",
        "apps.audit",
        "apps.integration"
    ])
    sys.exit(bool(failures))
