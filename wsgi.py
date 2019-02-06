"""
WSGI config for project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import locale
import os
import sys

from django.core.wsgi import get_wsgi_application


locale.setlocale(locale.LC_TIME, 'ru_RU.utf8')
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
application = get_wsgi_application()
