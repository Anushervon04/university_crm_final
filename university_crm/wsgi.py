"""
WSGI config for CRM Донишгоҳи Рақамикунонӣ 2025
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_crm.settings')

application = get_wsgi_application()
